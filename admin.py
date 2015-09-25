### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin as auth_UserAdmin
from django.contrib.auth.models import Group, User

from .models import Locker, LockerSetting, Submission, Comment


class DataLockerAdminSite(AdminSite):
    site_header = 'Data Locker Administration'
    site_url = '/datalocker'




class CommentAdmin(admin.ModelAdmin):
    list_display = ['id',
        'submission',
        'user',
        'timestamp',
        'comment',
        'parent_comment'
        ]


class LockerAdmin(admin.ModelAdmin):
    list_display = ['id',
        'form_url',
        'form_identifier',
        'owner',
        'name',
        'create_timestamp',
        'archive_timestamp'
        ]


class SettingAdmin(admin.ModelAdmin):
    list_display = ['category',
        'setting',
        'setting_identifier',
        'value',
        'locker'
        ]


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['id',
        'locker',
        'timestamp',
        'data',
        'deleted',
        'workflow_state'
        ]


class UserAdmin(auth_UserAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_staff',
        'is_superuser',
        )
    list_display_links = ('username', 'first_name', 'last_name')



admin_site = DataLockerAdminSite(name='datalockeradmin')

admin_site.register(Comment, CommentAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Locker, LockerAdmin)
admin_site.register(LockerSetting, SettingAdmin)
admin_site.register(Submission, SubmissionAdmin)
admin_site.register(User, UserAdmin)
