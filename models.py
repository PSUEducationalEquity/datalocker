from datetime import datetime
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
        return self.filter(archive_timestamp = None)


    def archive(self):
        return self.filter(archive_timestamp__isnull = False)


    def has_access(self, user):
        return self.filter(user = user)


    def is_archived(self):
        pass


##
# Models
##

class Locker(models.Model):
    form_url = models.CharField(max_length=255)
    form_identifier = models.CharField(max_length=255)
    user  = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    submitted_timestamp = models.DateTimeField(
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
        return self.form_identifier


    def is_archived(self):
        if archive_timestamp is None:
            return False
        return True


class LockerSettings(models.Model):
    category = models.CharField(max_length=255)
    setting = models.CharField(max_length=255)
    setting_identifier = models.SlugField()
    value = models.TextField()


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

    def __long__(self):
        return 'Submission: ' + self.id
    locker = models.ForeignKey(Locker,
        db_column="form_identifier",
        related_name="Submission_locker",
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
