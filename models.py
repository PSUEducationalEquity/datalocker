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

    def enable_discussion(self,enable=None):
        discussion_setting, created =LockerSetting.objects.get_or_create(
            category='discussion',
            setting_identifier='discussion-enabled',
            locker=self,
            defaults={
                'setting': 'Indicates if discussion is enabled or not',
                'value': False,
                }
            )
        # import pdb; pdb.set_trace()
        if enable is None:
            return True if discussion_setting.value == 'True' else False
        elif enable in (True, False):
            discussion_setting.value = str(enable)
            discussion_setting.save()

    def enable_workflow(self, enable=None):
        workflow_setting, created = LockerSetting.objects.get_or_create(
            category='workflow',
            setting_identifier='workflow-enabled',
            locker=self,
            defaults={
                'setting': 'Indicates if workflow is enabled or not',
                'value': False,
                }
            )
        if enable is None:
            return True if workflow_setting.value == 'True' else False
        elif enable in (True, False):
            workflow_setting.value = str(enable)
            workflow_setting.save()


    def is_archived(self):
        if archive_timestamp is None:
            return False
        return True


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


    def get_all_states(self):
        try:
            all_states_setting = self.settings.get(
                category='workflow',
                setting_identifier='states',
                locker=self,
                )
        except LockerSetting.DoesNotExist:
            all_states = []
        else:
            all_states = json.loads(all_states_setting.value)
        return all_states


    def get_default_state(self):
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
        return {
            'workflow|enabled': self.enable_workflow(),
            'workflow|users-can-edit': self.workflow_users_can_edit(),
            'workflow|states': self.get_all_states(),
            'discussion|enabled': self.enable_discussion(),
            'discussion|users-have-access-to-disccusion': self.discussion_users_have_access(),
            'access|shared-users': self.shared_users_receive_email(),
            }



    def has_access(self, user):
        """

        """
        if user.username == self.owner:
            return True
        elif user in self.users.all():            
            return True
        return False


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


    def save_states(self, states):
        saved_state_setting, created = LockerSetting.objects.get_or_create(
            category='workflow',
            setting_identifier='states',
            locker=self,
            defaults={
                'setting': 'User-defined list of workflow states',
                }
            )
        saved_state_setting.value = json.dumps(
            [ item.strip() for item in states.split("\n") if item.strip() ]
            )
        saved_state_setting.save()


    def workflow_users_can_edit(self, enable=None):
        users_can_edit_setting, created = LockerSetting.objects.get_or_create(
            category='workflow',
            setting_identifier='users-can-edit',
            locker=self,
            defaults={
                'setting': 'Indicates if users can edit workflow',
                'value': False,
                }
            )
        if enable is None:
            return True if users_can_edit_setting.value == 'True' else False
        elif enable in (True, False):
            users_can_edit_setting.value = str(enable)
            users_can_edit_setting.save()


    def discussion_users_have_access(self, enable=None):
        discussion_users_have_access_setting, created = LockerSetting.objects.get_or_create(
            category='discussion',
            setting_identifier='users-have-access-to-disccusion',
            locker=self,
            defaults={
                'setting': 'Indicates if users have access to discussion',
                'value': False,
                }
            )
        if enable is None:
            return True if discussion_users_have_access_setting.value == 'True' else False
        elif enable in (True, False):
            discussion_users_have_access_setting.value = str(enable)
            discussion_users_have_access_setting.save()

    def shared_users_receive_email(self, enable=None):
        shared_users_receive_email_setting, created = LockerSetting.objects.get_or_create(
            category='email_users',
            setting_identifier='shared-users-will-receive-email',
            locker=self,
            defaults={
                'setting': 'Indicates shared users will receive an email when a new submission is submitted',
                'value': False,
                }
            )
        if enable is None:
            return True if shared_users_receive_email_setting.value == 'True' else False
        elif enable in (True, False):
            shared_users_receive_email_setting.value = str(enable)
            shared_users_receive_email_setting.save()




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


    def __str__(self):
        return str(self.locker)

    def __unicode__ (self):
        return str(self.id)


    def data_dict(self):
        """
        Returns the data field as an ordered dictionary instead of JSON
        """
        data = json.loads(self.data, object_pairs_hook=OrderedDict)
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
        Searches through all the submissions in the database for the indicated
        Locker and it will order them by timestamp and filter the first one with
        a newer timestamp. If there isn't one newer it will return the current
        Locker object to avoid and Index Out of Range Error.
        """
        try:
            nextSubmission = Submission.objects.filter(
                locker=self.locker,
                timestamp__gt=self.timestamp, deleted=None).order_by('timestamp')[0]
        except IndexError:
            nextSubmission = Submission.objects.filter(
                locker=self.locker, deleted=None).order_by('-timestamp')[0]
        return nextSubmission.id


    def older(self):
        """
        Searches through all the submissions in the database for the indicated
        Locker and it will order them by descending timestamp and filter
        the first one with an older timestamp. If there isn't an older one it
        will return the current Locker object to avoid and Index Out of Range Error.
        """
        try:
            lastSubmission = Submission.objects.filter(
                locker=self.locker,
                timestamp__lt=self.timestamp, deleted=None).order_by('-timestamp')[0]
        except IndexError:
            lastSubmission = Submission.objects.filter(
                locker=self.locker, deleted=None).order_by('timestamp')[0]
        return lastSubmission.id


    def oldest(self):
        """
        Searches through all the submissions in the database for the indicated
        Locker and it will order them by timestamp and filter the Locker object
        with the earliest timestamp.
        """
        oldestSubmission = Submission.objects.filter(
            locker=self.locker, deleted=None).earliest('timestamp')
        return oldestSubmission.id


    def newest(self):
        """
        Searches through all the submissions in the database for the indicated
        Locker and it will order them by timestamp and filter the Locker object
        with the newest timestamp.
        """
        newestSubmission = Submission.objects.filter(
            locker=self.locker, deleted=None).latest('timestamp')
        return newestSubmission.id




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
        return str(self.id)


    def is_editable(self):
        """
        Captures the current time and compares it to the timestamp
        on the submission the submissions. editable is returned True
        if the difference is within the timeframe set by COMMENT_EDIT_MAX
        """
        time = timezone.now()
        editTimeFrame = datetime.timedelta(minutes=settings.COMMENT_EDIT_MAX)
        editable = True if ((time - self.timestamp) < editTimeFrame) else False
        return editable


    def to_dict(self):
        """
        Returns the entire object as a Python dictionary
        """
        result = model_to_dict(self)
        result['editable'] = self.is_editable()
        result['color'] = "red"
        return result
