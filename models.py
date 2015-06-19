from django.db import models
from django.forms.models import model_to_dict
from django.utils import timezone

import datetime


# Create your models here.
class Locker(models.Model):
    pass
# Model used for the actual Submission of the form
# Needs to include the locer name, Submission timestamp,
# the data that is on the form and then it is needed to be returned readable
class Submission(models.Model):
    locker = models.ForeignKey(Locker)
    timestamp = models.DateTimeField()
    data = models.CharField()


    def data_dict(self):
        return data.to_dict()


    def to_dict(self):
        return model_to_dict(Submission)


# Model to show the owner/user_id of an added locker
class LockerUser(models.Model):
    locker = models.ForeignKey(Locker)
    user_id = models.ForeignKey(Locker)
