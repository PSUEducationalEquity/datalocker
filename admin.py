from django.contrib import admin
from .models import Locker, Submission

# Register your models here.
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id','locker','timestamp','data']


class LockerAdmin(admin.ModelAdmin):
    list_display = ['id','form_url','form_identifier','owner','name','create_timestamp','archive_timestamp']

admin.site.register(Locker, LockerAdmin)
admin.site.register(Submission, SubmissionAdmin)