### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.contrib.auth.models import User, Group
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from django.http import request
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.query import QuerySet

from collections import OrderedDict

import datetime, json


##
# Model Managers
##

class LockerQuerySet(models.query.QuerySet):
    def active(self):
        """
        If the locker  doesn't have an archived timestamp,
        the locker is active
        """
        return self.filter(archive_timestamp = None)


    def archived(self):
        """
        If the locker does have an archived timestamp,
        then the locker is archived
        """
        return self.filter(archive_timestamp__isnull = False)


    def has_access(self, user):
        """
        Filters the lockers such that the user specified must be the owner or
        user of the locker to be included
        """
        return Locker.objects.filter(Q(owner=user) | Q(users=user)).distinct()




class LockerManager(models.Manager):
    def get_query_set(self):
        return LockerQuerySet(self.model, using=self._db)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__,attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)




class SubmissionManager(models.Manager):
    def oldest(self, locker):
        """
        Returns the oldest submission based on the timestamp
        """
        try:
            return self.filter(
                locker=locker, deleted=None
                ).earliest('timestamp')
        except Submission.DoesNotExist:
            return None


    def newest(self, locker):
        """
        Returns the newest submission based on the timestamp
        """
        try:
            return self.filter(
                locker=locker, deleted=None
                ).latest('timestamp')
        except Submission.DoesNotExist:
            return None




##
# Models
##

class Locker(models.Model):
    form_url = models.CharField(
        max_length=255,
        default='',
        blank=True,
        )
    form_identifier = models.CharField(
        max_length=255,
        default='',
        blank=True,
        )
    name = models.CharField(
        max_length=255,
        default='',
        blank=True,)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='lockers_owned',
        default=None,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_lockers',
        blank=True,
        )
    create_timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
        )
    archive_timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        editable=False,
        default=None,
        blank=True,
        null=True,
        )
    objects = LockerManager()


    def __str__(self):
        return self.name


    def discussion_enabled(self, enable=None):
        """
        Gets or sets the discussion enabled setting on the locker.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='discussion',
            identifier='enabled',
            setting='Indicates if discussion is enabled or not',
            value=False
            )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()


    def discussion_users_have_access(self, enable=None):
        """
        Gets or sets the discussion setting on the locker indicating if shared
        users have access to the discussion.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='discussion',
            identifier='users-have-access',
            setting='Indicates if users have access to discussion',
            value=False
            )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()


    def fields_all(self):
        """
        Returns a list of all the fields that appear in any of the
        form submissions
        """
        all_fields_setting, created = self._get_or_create_setting(
            category='fields-list',
            identifier='all-fields',
            setting='List of all fields',
            value=json.dumps([])
            )
        all_fields = json.loads(all_fields_setting.value)
        is_dirty = False

        # include 'Workflow state' if workflow is enabled
        if self.workflow_enabled():
            if 'Workflow state' not in all_fields:
                all_fields.append('Workflow state')
                is_dirty = True
        else:
            try:
                all_fields.remove('Workflow state')
            except ValueError:
                pass
            else:
                is_dirty = True

        # see if there are new submissions to review
        last_updated_setting, created = self._get_or_create_setting(
            category='fields-list',
            identifier='last-updated',
            setting='Date/time all fields list last updated',
            value=timezone.now()
            )
        if created:
            submissions = self.submissions.all()
        else:
            submissions = self.submissions.filter(
                timestamp__gte=last_updated_setting.value)
        for submission in submissions:
            fields = submission.data_dict().keys()
            for field in fields:
                if not field in all_fields:
                    all_fields.append(field)
                    is_dirty = True

        # save the changes
        if is_dirty:
            all_fields_setting.value = json.dumps(all_fields)
            all_fields_setting.save()
            last_updated_setting.value = timezone.now()
            last_updated_setting.save()
        return all_fields


    def fields_selected(self, fields=None):
        """
        Gets/sets the list of fields to display for a submissions list

        If `fields` is None:

            Returns a list of fields the user selected to be displayed as part
            of the list of submissions

        If `fields` is specified:

            Validates and saves the list of selected fields to display.
            Validation involves ensuring there is a match between each specified
            field and the list of all fields possible for this locker.

            `fields` is a list of field names or slugified field names.
        """
        setting, created = self._get_or_create_setting(
            category='fields-list',
            identifier='selected-fields',
            setting='User-defined list of fields to display in tabular view',
            value=json.dumps([])
            )
        if fields is None:
            return json.loads(setting.value)
        else:
            selected_fields = []
            for field in self.fields_all():
                if field in fields or slugify(field) in fields:
                    selected_fields.append(field)
            setting.value = json.dumps(selected_fields)
            setting.save()


    def _get_or_create_setting(self, category, identifier, setting, value):
        """
        Gets or creates a setting from the current object's `settings` field.
        """
        try:
            setting = self.settings.get(
                category=category,
                identifier=identifier
                )
        except LockerSetting.DoesNotExist:
            setting = LockerSetting(
                category=category,
                identifier=identifier,
                locker=self,
                setting=setting,
                value=value
                )
            setting.save()
            self.settings.add(setting)
            self.save()
            return (setting, True)
        else:
            return (setting, False)


    def get_settings(self):
        """
        Returns a dictionary of all the locker's settings
        """
        settings_dict = {}
        for setting in self.settings.all():
            key = "%s|%s" % (setting.category, setting.identifier)
            try:
                value = json.loads(setting.value)
            except:
                if setting.value == "False":
                    value = False
                elif setting.value == "True":
                    value = True
                else:
                    value = setting.value
            settings_dict[key] = value
        return settings_dict


    def has_access(self, user):
        """
        Returns a boolean indicating if the specified user has access to the
        locker as either the owner, a shared user, or a super user.
        """
        return self.is_owner(user) or self.is_user(user) or user.is_superuser


    def is_archived(self):
        """
        Returns a boolean indicating if the locker has been archived
        """
        if archive_timestamp is None:
            return False
        return True


    def is_owner(self, user):
        """
        Returns a boolean indicating if the specified user is the locker owner
        """
        return user == self.owner


    def is_user(self, user):
        """
        Returns a boolean indicating if the specified user has shared access
        to the locker
        """
        return user in self.users.all()


    def shared_users_notification(self, enable=None):
        """
        Gets or sets the setting on the locker indicating if shared users
        receive an email when a new submission is received.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='submission-notifications',
            identifier='notify-shared-users',
            setting='Indicates if shared users should receive an ' \
                'email when a new submission is received',
            value=False
            )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()


    def workflow_default_state(self):
        states = self.workflow_states()
        try:
            return states[0]
        except:
            return ''


    def workflow_enabled(self, enable=None):
        """
        Gets or sets the workflow enabled setting on the locker.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='workflow',
            identifier='enabled',
            setting='Indicates if workflow is enabled or not',
            value=False
            )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()
            if not enable:
                # remove the workflow state from the selected fields list
                fields = self.fields_selected()
                try:
                    fields.remove("Workflow state")
                except ValueError:
                    pass
                else:
                    self.fields_selected(fields)


    def workflow_states(self, states=None):
        """
        Gets or sets the workflow setting on the locker indicating the possible
        workflow states.

        Calling it with enable=None will return the current setting value
        as a list.
        Passing it a list of values, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='workflow',
            identifier='states',
            setting='User-defined list of workflow states',
            value=json.dumps([])
            )
        if states is None:
            return json.loads(setting.value)
        else:
            setting.value = json.dumps(
                [ item.strip() for item in states.split("\n") if item.strip() ]
                )
            setting.save()


    def workflow_users_can_edit(self, enable=None):
        """
        Gets or sets the workflow setting on the locker indicating if shared
        users can change the workflow state.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='workflow',
            identifier='users-can-edit',
            setting='Indicates if users can change the workflow state',
            value=False
            )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()




class LockerSetting(models.Model):
    category = models.CharField(
        max_length=255,
        )
    setting = models.CharField(
        max_length=255,
        )
    identifier = models.SlugField()
    value = models.TextField(
        default='',
        )
    locker = models.ForeignKey(
        Locker,
        related_name="settings",
        on_delete=models.CASCADE,
        )




class Submission(models.Model):
    locker = models.ForeignKey(
        Locker,
        related_name="submissions",
        on_delete=models.CASCADE,
        )
    timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
        )
    data = models.TextField(
        default='',
        blank=True,
        )
    deleted = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        editable=False,
        default=None,
        blank=True,
        null=True,
        )
    workflow_state = models.CharField(
        max_length=255,
        default='',
        blank=True,
        )
    objects = SubmissionManager()


    def __str__(self):
        return "%s to %s" % (self.timestamp, self.locker)


    def data_dict(self, with_types=False):
        """
        Returns the data field as an ordered dictionary
        """
        try:
            data = json.loads(self.data, object_pairs_hook=OrderedDict)
        except ValueError:
            data = {}
        if with_types:
            for key, value in data.iteritems():
                if isinstance(value, list):
                    value_type = 'list'
                elif isinstance(value, dict) or isinstance(value, OrderedDict):
                    value_type = 'dict'
                else:
                    value_type = 'string'
                data[key] = { 'value': value, 'type': value_type }
        return data


    def to_dict(self):
        """
        Returns the entire object as a Python dictionary
        """
        result = model_to_dict(self)
        result['data'] = self.data_dict()
        # model_to_dict skips fields that are not editable and fields that have
        # auto_now_add=True are considered not editable, thus we add the
        # submission timestamp back in manually
        result['timestamp'] = self.timestamp.isoformat()
        result['deleted'] = self.deleted.isoformat() if self.deleted else None
        result['purge_date'] = self.purge_date
        return result


    def newer(self):
        """
        Returns the submission object that was submitted immediately after
        this one. If there isn't a newer submission, the current submission is
        returned.
        """
        try:
            nextSubmission = Submission.objects.filter(
                locker=self.locker,
                timestamp__gt=self.timestamp,
                deleted=None
                ).order_by('timestamp')[0]
        except IndexError:
            return self
        else:
            return nextSubmission


    def older(self):
        """
        Returns the submission object that was submitted immediately before
        this one. If there isn't an older submission, the current submission is
        returned.
        """
        try:
            prevSubmission = Submission.objects.filter(
                locker=self.locker,
                timestamp__lt=self.timestamp,
                deleted=None
                ).order_by('-timestamp')[0]
        except IndexError:
            return self
        else:
            return prevSubmission


    @property
    def purge_date(self):
        """
        Returns the date that the submission should be purged from the system
        """
        if self.deleted is None:
            return None
        return self.deleted + datetime.timedelta(
                days=settings.SUBMISSION_PURGE_DAYS
                )




class Comment(models.Model):
    submission = models.ForeignKey(
        Submission,
        related_name="comments",
        on_delete=models.CASCADE,
        )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.PROTECT,
        )
    timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
        )
    comment = models.TextField(
        default='',
        blank=True,
        )
    parent = models.ForeignKey(
        'self',
        related_name="children",
        default=None,
        blank=True,
        null=True,
        )


    def __str__(self):
        return "%s in %s by %s" % (
            self.submission.timestamp,
            self.submission.locker,
            self.user
            )


    @property
    def is_editable(self):
        """
        Indicates if the comment is editable because it was created within
        COMMENT_EDIT_MAX time till now.
        """
        oldest_timestamp = timezone.now()
        oldest_timestamp -= datetime.timedelta(minutes=settings.COMMENT_EDIT_MAX)
        return True if (self.timestamp > oldest_timestamp) else False


    def to_dict(self):
        """
        Returns the entire object as a Python dictionary
        """
        result = model_to_dict(self)
        result['editable'] = self.is_editable
        # model_to_dict skips fields that are not editable and fields that have
        # auto_now_add=True are considered not editable, thus we add the
        # submission timestamp back in manually
        result['timestamp'] = self.timestamp.isoformat()
        result['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
            }
        return result
