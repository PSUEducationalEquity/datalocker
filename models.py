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
        return self.filter(
            locker=locker, deleted=None
            ).earliest('timestamp')


    def newest(self, locker):
        """
        Returns the newest submission based on the timestamp
        """
        return self.filter(
            locker=locker, deleted=None
            ).latest('timestamp')




##
# Models
##

class Locker(models.Model):
    form_url = models.CharField(max_length=255)
    form_identifier = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    users = models.ManyToManyField(
        User,
        related_name='lockers',
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
        null=True,
        blank=True,
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
        setting, created = LockerSetting.objects.get_or_create(
            category='discussion',
            setting_identifier='enabled',
            locker=self,
            defaults={
                'setting': 'Indicates if discussion is enabled or not',
                'value': False,
                }
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
        setting, created = LockerSetting.objects.get_or_create(
            category='discussion',
            setting_identifier='users-have-access',
            locker=self,
            defaults={
                'setting': 'Indicates if users have access to discussion',
                'value': False,
                }
            )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()


    def get_all_fields_list(self):
        """
        This gets all of the fields that were submitted to the form
        """
        try:
            all_fields_setting = self.settings.get(
                category='fields-list',
                setting_identifier='all-fields'
                )
        except LockerSetting.DoesNotExist:
            all_fields = []
        else:
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
        try:
            last_updated_setting = self.settings.get(
                category='fields-list',
                setting_identifier='last-updated'
                )
        except LockerSetting.DoesNotExist:
            submissions = self.submissions.all()
        else:
            submissions = self.submissions.filter(
                timestamp__gte=last_updated_setting.value)

        for submission in submissions:
            fields = submission.data_dict().keys()
            for field in fields:
                if not field in all_fields:
                    all_fields.append(field)
        try:
            all_fields_setting.value = json.dumps(all_fields)
        except UnboundLocalError:
            all_fields_setting = LockerSetting(
                category='fields-list',
                setting='List of all fields',
                setting_identifier='all-fields',
                value=json.dumps(all_fields),
                locker=self,
                )
        all_fields_setting.save()
        try:
            last_updated_setting.value = timezone.now()
        except UnboundLocalError:
            last_updated_setting = LockerSetting(
                category='fields-list',
                setting='Date/time all fields list last updated',
                setting_identifier='last-updated',
                value=timezone.now(),
                locker=self,
                )
        last_updated_setting.save()
        return all_fields


    def get_default_workflow_state(self):
        states = self.get_all_states()
        try:
            return states[0]
        except:
            return ''


    def get_selected_fields_list(self):
        """
        Get's the selected fields off of the Submission List Page,
        and inserts them into the table
        """
        try:
            selected_fields_setting = self.settings.get(
                category='fields-list',
                setting_identifier='selected-fields'
                )
        except LockerSetting.DoesNotExist:
            selected_fields = []
        else:
            selected_fields = json.loads(selected_fields_setting.value)
        return selected_fields


    def get_settings(self):
        """
        Returns a dictionary of all the locker's settings
        """
        settings_dict = {}
        settings = LockerSetting.objects.filter(locker=self)
        for setting in settings:
            key = "%s|%s" % (setting.category, setting.setting_identifier)
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
        locker as either the owner or a shared user.
        """
        if user.username == self.owner:
            return True
        elif user in self.users.all():
            return True
        return False


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
        return True if user.username == self.owner else False


    def is_user(self, user):
        """
        Returns a boolean indicating if the specified user has shared access
        to the locker
        """
        return True if user in self.users else False


    def save_selected_fields_list(self, fields):
        selected_fields = []
        for field in self.get_all_fields_list():
            if slugify(field) in fields:
                selected_fields.append(field)
        selected_fields_setting, created = LockerSetting.objects.get_or_create(
            category='fields-list',
            setting_identifier='selected-fields',
            locker=self,
            defaults={
                'setting': 'User-defined list of fields to display in tabular view',
                }
            )
        selected_fields_setting.value = json.dumps(selected_fields)
        selected_fields_setting.save()


    def shared_users_notification(self, enable=None):
        """
        Gets or sets the setting on the locker indicating if shared users
        receive an email when a new submission is received.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = LockerSetting.objects.get_or_create(
            category='submission-notifications',
            setting_identifier='notify-shared-users',
            locker=self,
            defaults={
                'setting': 'Indicates if shared users should receive an ' \
                    'email when a new submission is received',
                'value': False,
                }
            )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()


    def workflow_enabled(self, enable=None):
        """
        Gets or sets the workflow enabled setting on the locker.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = LockerSetting.objects.get_or_create(
            category='workflow',
            setting_identifier='enabled',
            locker=self,
            defaults={
                'setting': 'Indicates if workflow is enabled or not',
                'value': False,
                }
            )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()


    def workflow_states(self, states=None):
        """
        Gets or sets the workflow setting on the locker indicating the possible
        workflow states.

        Calling it with enable=None will return the current setting value
        as a list.
        Passing it a list of values, will set the value.
        """
        setting, created = LockerSetting.objects.get_or_create(
            category='workflow',
            setting_identifier='states',
            locker=self,
            defaults={
                'setting': 'User-defined list of workflow states',
                'value': json.dumps([]),
                }
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
        setting, created = LockerSetting.objects.get_or_create(
            category='workflow',
            setting_identifier='users-can-edit',
            locker=self,
            defaults={
                'setting': 'Indicates if users can change the workflow state',
                'value': False,
                }
            )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()




class LockerSetting(models.Model):
    category = models.CharField(max_length=255)
    setting = models.CharField(max_length=255)
    setting_identifier = models.SlugField()
    value = models.TextField()
    locker = models.ForeignKey(
        Locker,
        related_name="settings",
        on_delete=models.PROTECT,
        )



##
# Model used for the actual Submission of the form
# Needs to include the locer name, Submission timestamp,
# the data that is on the form and then it is needed to be returned readable
##

class Submission(models.Model):
    locker = models.ForeignKey(
        Locker,
        db_column="form_identifier",
        related_name="submissions",
        on_delete=models.PROTECT,
        )
    timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        )
    data = models.TextField(blank=True)
    deleted = models.DateTimeField(
        blank=True,
        null=True,
        )
    workflow_state = models.CharField(
        max_length=25,
        default='Unreviewed',
        )
    objects = SubmissionManager()


    def __str__(self):
        return "%s to %s" % (self.timestamp, self.locker)


    def data_dict(self):
        """
        Returns the data field as an ordered dictionary
        """
        try:
            data = json.loads(self.data, object_pairs_hook=OrderedDict)
        except ValueError:
            data = {}
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
        reutrned.
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




class Comment(models.Model):
    submission = models.ForeignKey(
        Submission,
        related_name="comments",
        on_delete=models.PROTECT,
        )
    user = models.ForeignKey(
        User,
        related_name="comment_user",
        )
    timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
        )
    comment = models.TextField(blank=True)
    parent_comment = models.ForeignKey(
        'self',
        related_name="comment_parent",
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
