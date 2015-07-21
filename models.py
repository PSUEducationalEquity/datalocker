###Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###
from django.contrib.auth.models import User, Group
from django.db import models
from django.forms.models import model_to_dict
from django.http import request
from django.utils import timezone
from django.db.models.query import QuerySet

from collections import OrderedDict

from .models import User

import datetime, json



##
# Model Managers
##

class LockerQuerySet(models.query.QuerySet):
    def active(self):
        return self.filter(archive_timestamp = None)


    def archived(self):
        return self.filter(archive_timestamp__isnull = False)


    def has_access(self, user):
        """
        We will need to know the id of the user from the auth_user table.
        We will then need to cross reference that user id
        with the allowed user id in the datalocker_locker_user table
        """
        if user.is_authenticated():
            return Locker.objects.filter(owner=user) | Locker.objects.filter(users=user)
        else:
            return Locker.objects.filter(owner=user)




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
        try:
            all_fields_setting = self.settings.get(category='fields-list', setting_identifier='all-fields')
        except LockerSetting.DoesNotExist:
            all_fields = []
        else:
            all_fields = json.loads(all_fields_setting.value)

        try:
            last_updated_setting = self.settings.get(category='fields-list', setting_identifier='last-updated')
        except LockerSetting.DoesNotExist:
            submissions = self.submissions.all()
        else:
            submissions = self.submissions.filter(timestamp__gte=last_updated_setting.value)

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
            last_updated_setting.value = datetime.datetime.now()
        except UnboundLocalError:
            last_updated_setting = LockerSetting(
                category='fields-list',
                setting='Date/time all fields list last updated',
                setting_identifier='last-updated',
                value=datetime.datetime.now(),
                locker=self,
                )
        last_updated_setting.save()
        return all_fields


    def get_selected_fields_list(self):
        try:
            selected_fields_setting = self.settings.get(category='fields-list', setting_identifier='selected-fields')
        except LockerSetting.DoesNotExist:
            selected_fields = []
        else:
            selected_fields = json.loads(selected_fields_setting.value)
        return selected_fields




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


    def __str__(self):
        return str(self.locker)


    def data_dict(self):
        data = json.loads(self.data, object_pairs_hook=OrderedDict)
        return data


    def to_dict(self):
        result = model_to_dict(self)
        result['data'] = self.data_dict()
        return result


    def newer(self):
        try:
            nextSubmission = Submission.objects.filter(locker=self.locker, id__gt=self.id)[0]
        except IndexError:
            nextSubmission = Submission.objects.filter(locker=self.locker).order_by('-id')[0]
        return nextSubmission.id


    def older(self):
        try:
            lastSubmission = Submission.objects.filter(locker=self.locker, id__lt=self.id).order_by('-id')[0]
        except IndexError:
            lastSubmission = Submission.objects.filter(locker=self.locker).order_by('id')[0]
        return lastSubmission.id


    def oldest(self):
        oldestSubmission = Submission.objects.filter(locker=self.locker).order_by('id')[0]
        return oldestSubmission.id


    def newest(self):
        newestSubmission = Submission.objects.filter(locker=self.locker).order_by('-id')[0]
        return newestSubmission.id
