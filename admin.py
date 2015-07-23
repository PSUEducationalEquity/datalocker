###Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group, User

from .models import Locker, LockerSetting, Submission


class DataLockerAdminSite(AdminSite):
    site_header = 'Data Locker Administration'
    site_url = '/datalocker'




# Register your models here.
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id','locker','timestamp','data','deleted']




class LockerAdmin(admin.ModelAdmin):
    list_display = ['id','form_url','form_identifier','owner','name','create_timestamp','archive_timestamp']




class SettingAdmin(admin.ModelAdmin):
    list_display = ['category','setting','setting_identifier','value','locker']




class UserAdmin(admin.ModelAdmin):
    list_display = ['id','username','email','first_name','last_name','is_superuser','is_staff']

admin_site = DataLockerAdminSite(name = 'datalockeradmin')
admin_site.register(Group, GroupAdmin)
admin_site.register(Locker, LockerAdmin)
admin_site.register(Submission, SubmissionAdmin)
admin_site.register(LockerSetting, SettingAdmin)
admin_site.register(User, UserAdmin)
