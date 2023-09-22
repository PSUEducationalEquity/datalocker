### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth.admin import GroupAdmin, UserAdmin as auth_UserAdmin
from django.contrib.auth.models import Group, User

from .decorators import never_cache
from .models import Locker, LockerSetting, Submission, Comment


class ArchivedFilter(admin.SimpleListFilter):
    """Filters the list based on archived_timestamp value

    Extends:
        admin.SimpleListFilter

    Variables:
        title {str} -- Name that will be displayed for the filter
        parameter_name {str} -- [description]
    """
    title = 'Archived'
    parameter_name = 'archived'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Yes'),
            ('no', 'No'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(archive_timestamp=None)
        elif self.value() == 'yes':
            return queryset.exclude(archive_timestamp=None)
        else:
            return queryset


class DeletedFilter(admin.SimpleListFilter):
    """Filters the list based on deleted value

    Extends:
        admin.SimpleListFilter

    Variables:
        title {str} -- Name that will be displayed for the filter
        parameter_name {str} -- [description]
    """
    title = 'Deleted'
    parameter_name = 'is_deleted'

    def lookups(self, request, model_admin):
        return [
            ('yes', 'Yes'),
            ('no', 'No'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'no':
            return queryset.filter(deleted=None)
        elif self.value() == 'yes':
            return queryset.exclude(deleted=None)
        else:
            return queryset


class DataLockerAdminSite(AdminSite):
    site_header = 'Data Locker Administration'

    def admin_view(self, view, cacheable=False):
        view_function = super(DataLockerAdminSite, self).admin_view(view, cacheable)  # NOQA
        return never_cache(view_function)

    @never_cache
    def app_index(self, request, app_label, extra_context=None):
        return super(DataLockerAdminSite, self).app_index(request, app_label, extra_context)  # NOQA

    @never_cache
    def index(self, request, extra_context=None):
        return super(DataLockerAdminSite, self).index(request, extra_context)

    @never_cache
    def login(self, request, extra_context=None):
        return super(DataLockerAdminSite, self).login(request, extra_context)

    @never_cache
    def logout(self, request, extra_context=None):
        return super(DataLockerAdminSite, self).logout(request, extra_context)

    @never_cache
    def password_change(self, request, extra_context=None):
        return super(DataLockerAdminSite, self).password_change(request, extra_context)  # NOQA

    @never_cache
    def password_change_done(self, request, extra_context=None):
        return super(DataLockerAdminSite, self).password_change_done(request, extra_context)  # NOQA


# class CommentAdmin(admin.ModelAdmin):
#     list_display = [
#         'id',
#         'submission',
#         'user',
#         'timestamp',
#         'comment',
#         'parent'
#     ]


class LockerAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [
            'name',
            'form_identifier',
            'form_url',
            'owner',
            'users',
            'create_timestamp',
            'archive_timestamp'
        ]}),
    ]
    list_display = [
        'name',
        'owner',
        'form_identifier',
        'form_url',
        'archived'
    ]
    list_display_links = ['name']
    list_filter = [ArchivedFilter, 'owner']
    readonly_fields = ['create_timestamp', 'archive_timestamp']

    def archived(self, obj):
        return obj.archive_timestamp is not None
    archived.boolean = True


class LockerSettingAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': [
            'locker',
            'category',
            'identifier',
            'setting',
            'value',
        ]}),
    ]
    list_display = [
        'locker',
        'category',
        'identifier',
        'setting',
        'value',
    ]
    list_display_links = ['identifier', 'setting']
    list_filter = ['category', 'identifier', 'locker']


class SubmissionAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    fieldsets = [
        (None, {'fields': [
            'locker',
            'data',
            'workflow_state',
            'deleted',
            'timestamp',
        ]}),
    ]
    list_display = [
        'id',
        'locker',
        'workflow_state',
        'timestamp',
        'is_deleted',
    ]
    list_filter = [DeletedFilter, 'workflow_state', 'locker']
    readonly_fields = ['deleted', 'timestamp']

    def is_deleted(self, obj):
        return obj.deleted is not None
    is_deleted.boolean = True
    is_deleted.admin_order_field = 'deleted'


class UserAdmin(auth_UserAdmin):
    actions = [
        'user_make_active',
        'user_make_inactive',
        'user_make_staff',
        'user_make_notstaff',
    ]
    date_hierarchy = 'last_login'
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_active',
        'is_staff',
        'is_superuser',
        'last_login',
    )
    list_display_links = ('username', 'first_name', 'last_name')

    def user_make_active(self, request, queryset):
        rows_updated = queryset.update(is_active=True)
        if rows_updated == 1:
            msg = '1 user was'
        else:
            msg = f'{rows_updated} users were'
        self.message_user(request, f'{msg} successfully marked as active.')
    user_make_active.short_description = 'Mark selected users as active'

    def user_make_inactive(self, request, queryset):
        rows_updated = queryset.update(is_active=False)
        if rows_updated == 1:
            msg = '1 user was'
        else:
            msg = f'{rows_updated} users were'
        self.message_user(request, f'{msg} successfully marked as inactive.')
    user_make_inactive.short_description = 'Mark selected users as inactive'

    def user_make_staff(self, request, queryset):
        rows_updated = queryset.update(is_staff=True)
        if rows_updated == 1:
            msg = '1 user was'
        else:
            msg = f'{rows_updated} users were'
        self.message_user(request, f'{msg} successfully marked as staff.')
    user_make_staff.short_description = 'Mark selected users as staff'

    def user_make_notstaff(self, request, queryset):
        rows_updated = queryset.update(is_staff=False)
        if rows_updated == 1:
            msg = '1 user was'
        else:
            msg = f'{rows_updated} users were'
        self.message_user(request, f'{msg} successfully marked as not staff.')
    user_make_notstaff.short_description = 'Mark selected users as not staff'


admin_site = DataLockerAdminSite(name='datalockeradmin')

# admin_site.register(Comment, CommentAdmin)
admin_site.register(Group, GroupAdmin)
admin_site.register(Locker, LockerAdmin)
admin_site.register(LockerSetting, LockerSettingAdmin)
admin_site.register(Submission, SubmissionAdmin)
admin_site.register(User, UserAdmin)
