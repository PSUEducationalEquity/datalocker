from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone

import datetime


# Create your models here.
class Locker(models.Model):
    locker = models.CharField(max_length=250)
    user_id = models.CharField(max_length=250)
# Model used for the actual Submission of the form
# Needs to include the locer name, Submission timestamp,
# the data that is on the form and then it is needed to be returned readable
class Submission(models.Model):
    locker = models.ForeignKey(Locker)
    timestamp = models.DateTimeField(auto_now=False,
        auto_now_add=True
        )
    data = models.CharField(max_length=250)


    def data_dict(self):
        return self.to_dict()


    def to_dict(self):
        return model_to_dict(self)


# Model to show the owner/user_id of an added locker
class LockerUser(models.Model):
    locker = models.ForeignKey(Locker)
    user_id = models.ForeignKey(Locker)
