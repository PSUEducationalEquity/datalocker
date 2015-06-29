from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User

from .models import Locker, Submission


class DataLockerAdminSite(AdminSite):
    site_header = 'Data Locker Administration'
    site_url = '/datalocker'




# Register your models here.
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id','locker','timestamp','data']




class LockerAdmin(admin.ModelAdmin):
    list_display = ['id','form_url','form_identifier','owner','name','create_timestamp','archive_timestamp']


admin_site = DataLockerAdminSite(name = 'datalockeradmin')
admin_site.register(Group, GroupAdmin)
admin_site.register(Locker, LockerAdmin)
admin_site.register(Submission, SubmissionAdmin)
admin_site.register(User, UserAdmin)
