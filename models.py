from django.db import models
from django.utils import timezone 
from django.contrib.auth.models import User, Group



# Create your models here.
class User(models.Model):
    pass


# Locker class created 
class Locker(models.Model):
    form_url = models.CharField(max_length=255)
    form_identifier = models.CharField(max_length=255)
    user  = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    submitted_timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,)
    archive_timestamp = models.DateField(DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
        )


    objects = LockerManager()


#LockerManager class created 
class LockerManager(models.Manager):
    
    
    def active(self)	
        
    def archive(self) 
        pass  
    def has_access(User)
        pass
    def is_archived(self, reference_date=datetime.today()):
        try: submitted_timestamp = self.filter(
        
   
class LockerSettings(models.Model):
    category = model.CharField(max_length=255)
    setting = model.CharField(max_length=255)
    setting_identifier = models.SlugField()
    value = models.CharField(max_length=255)
    
