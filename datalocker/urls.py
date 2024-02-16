### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###

from django.conf import settings
from django.contrib.auth import views as auth_views
from django.urls import path

from datalocker import views


app_name = 'datalocker'
urlpatterns = [
    path('noaccess',
         views.no_access,
         name='no_access'),

    path('login',
         auth_views.LoginView.as_view(),
         name='app_login'),
    path('logout',
         auth_views.LogoutView.as_view(),
         name='app_logout'),
    path('password_change',
         auth_views.PasswordChangeView.as_view(),
         name='password_change'),
    path('password_change_done',
         auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),

    path('submission',
         views.form_submission_view,
         name='form_submission'),

    path('users',
         views.users_list,
         name='users_list'),

    path('(<int:locker_id>/archive',
         views.locker_archive,
         name='locker_archive'),
    path('(<int:locker_id>/modify',
         views.modify_locker,
         name='modify_locker'),
    path('(<int:locker_id>/unarchive',
         views.locker_unarchive,
         name='locker_unarchive'),

    path('(<int:locker_id>/submissions/add',
         views.submission_add,
         name='submission_add'),
    path('(<int:locker_id>/submissions/<int:submission_id>/delete',
         views.submission_delete,
         name='submission_delete'),
    path('(<int:locker_id>/submissions/<int:submission_id>/discussion/add',
         views.comment_add,
         name='comment_add'),
    path('(<int:locker_id>/submissions/<int:submission_id>/discussion/modify',
         views.comment_modify,
         name='comment_modify'),
    path('(<int:locker_id>/submissions/<int:submission_id>/discussion',
         views.comments_list,
         name='comments_list'),
    path('(<int:locker_id>/submissions/<int:submission_id>/undelete',
         views.submission_undelete,
         name='submission_undelete'),
    path('(<int:locker_id>/submissions/<int:submission_id>/workflow/modify',
         views.workflow_modify,
         name='workflow_modify'),
    path('(<int:locker_id>/submissions/<int:submission_id>',
         views.submission_view,
         name='submission_view'),
    path('(<int:locker_id>/submissions',
         views.submissions_list_view,
         name='submissions_list'),

    path('(<int:locker_id>/users',
         views.locker_users,
         name='locker_users'),
    path('(<int:locker_id>/users/add',
         views.locker_user_add,
         name='locker_user_add'),
    path('(<int:locker_id>/users/delete',
         views.locker_user_delete,
         name='locker_user_delete'),

    path('',
         views.locker_list_view,
         name='index'),
]

if settings.DEBUG:
    urlpatterns += [
        path('testing/400',
             views.testing_bad_request_view,
             name='testing_bad_request'),
        path('testing/403',
             views.testing_forbidden_view,
             name='testing_forbidden'),
        path('testing/404',
             views.testing_not_found_view,
             name='testing_not_found'),
        path('testing/500',
             views.testing_server_error_view,
             name='testing_server_error'),
    ]

##
# EXAMPLE Urls
#
# /datalocker
# /datalocker/#/submissions
# /datalocker/#/submissions/#/view
# /datalocker/#/settings
# /datalocker/#/submissions/#/comments
