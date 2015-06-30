from datetime import datetime
from django.contrib.auth.models import User, Group
from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone
from django.db.models.query import QuerySet

from collections import OrderedDict

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
        return self.filter(owner = user)





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




class LockerSetting(models.Model):
    category = models.CharField(max_length=255)
    setting = models.CharField(max_length=255)
    setting_identifier = models.SlugField()
    value = models.TextField()




# Model used for the actual Submission of the form
# Needs to include the locer name, Submission timestamp,
# the data that is on the form and then it is needed to be returned readable
class Submission(models.Model):
    locker = models.ForeignKey(
        Locker,
        db_column="form_identifier",
        related_name="submission",
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
        json = json.parse(Submission.data)
        return data, json


    def to_dict(self):
        result = model_to_dict(self)
        result['data'] = self.data_dict()
        return result
