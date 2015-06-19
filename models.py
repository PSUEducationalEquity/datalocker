from django.db import models
from django.froms.models import model_to_dict
from django.utils import timezone

import datetime


# Create your models here.
# Model used for the actual submission of the form
# Needs to include the locer name, Submission timestamp,
# the data that is on the form and then it is needed to be returned readable
class Submission(models.Model):
    locker = models.ForeignKey('Locker')
    timestamp = models.DateTimeField(auto_add_now=True)
    data = models.Text()
    model_to_dict(Submission)

class LockerUser(models.Model):
    locker = models.ForeignKey('Locker')
    user_id = models.ForeignKey('Locker')
