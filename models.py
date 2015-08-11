### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.contrib.auth.models import User, Group
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
                setting='states',
                setting_identifier='states',
                locker=self,
                )
        except LockerSetting.DoesNotExist:
            all_states = []
        else:
            all_states = json.loads(all_states_setting.value)
            all_states_setting.save()


    def get_selected_states(self):
        try:
            selected_state_setting = self.settings.get(
                category='workflow',
                setting='states',
                setting_identifier='states',
                locker=self,
                defaults={
                    'workflow': 'unreviewed',
                    }
                )
        except LockerSetting.DoesNotExist:
            selected_state = []
        else:
            selected_state = json.loads(selected_state_setting.value)
        return selected_state

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


    def has_access(self, user):
        """

        """
        if user == self.owner:
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
            setting='states',
            setting_identifier='states',
            locker=self,
            )
        saved_state_setting.value = json.dumps(selected_state)
        saved_state_setting.save()



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
        default='unreviewed',
        )


    def __str__(self):
        return str(self.locker)


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
                timestamp__gt=self.timestamp).order_by('timestamp')[0]
        except IndexError:
            nextSubmission = Submission.objects.filter(
                locker=self.locker).order_by('-timestamp')[0]
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
                timestamp__lt=self.timestamp).order_by('-timestamp')[0]
        except IndexError:
            lastSubmission = Submission.objects.filter(
                locker=self.locker).order_by('timestamp')[0]
        return lastSubmission.id


    def oldest(self):
        """
        Searches through all the submissions in the database for the indicated
        Locker and it will order them by timestamp and filter the Locker object
        with the earliest timestamp.
        """
        oldestSubmission = Submission.objects.filter(
            locker=self.locker).earliest('timestamp')
        return oldestSubmission.id


    def newest(self):
        """
        Searches through all the submissions in the database for the indicated
        Locker and it will order them by timestamp and filter the Locker object
        with the newest timestamp.
        """
        newestSubmission = Submission.objects.filter(
            locker=self.locker).latest('timestamp')
        return newestSubmission.id