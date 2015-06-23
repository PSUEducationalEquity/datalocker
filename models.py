from django.contrib.auth.models import User, Group
from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone

import datetime, json


##
# Model Managers
##

class LockerManager(models.Manager):
    def active(self):
        pass


    def archive(self):
        pass


    def has_access(User):
        pass


    def is_archived(self):
        pass




##
# Models
##

class Locker(models.Model):
    form_url = models.CharField(max_length=255)
    form_identifier = models.CharField(max_length=255)
    user  = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    submitted_timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
        )
    archive_timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
        )
    objects = LockerManager()


class LockerSettings(models.Model):
    category = models.CharField(max_length=255)
    setting = models.CharField(max_length=255)
    setting_identifier = models.SlugField()
    value = models.CharField(max_length=255)


# Model to show the owner/user_id of an added locker
class LockerUser(models.Model):
    locker = models.ForeignKey(Locker,
        related_name="locker_user",
        on_delete=models.PROTECT,
        )
    user_id = models.ForeignKey(Locker,
        related_name="LockerUser",
        on_delete=models.PROTECT,
        )


# Model used for the actual Submission of the form
# Needs to include the locer name, Submission timestamp,
# the data that is on the form and then it is needed to be returned readable
class Submission(models.Model):
    locker = models.ForeignKey(Locker,
        related_name="Submission",
        on_delete=models.PROTECT,
        )
    timestamp = models.DateTimeField(auto_now=False,
        auto_now_add=True,
        )
    data = models.TextField(blank=True)


    def data_dict(self):
        return json.loads(self.data)


    def to_dict(self):
        result = model_to_dict(self)
        import pdb; pdb.set_trace()
        result['data'] = self.data_dict()
        return result


class User(models.Model):
    pass
