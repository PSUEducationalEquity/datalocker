###Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###

from django.conf import settings
from django.conf.urls import patterns, url

from datalocker import views


urlpatterns = patterns('',
    url(r'^$',
        views.locker_list_view,
        name='index',
        ),
    url(r'^login$',
        views.login,
        name="app_login"
        ),
    url(r'^logout$',
        views.logout,
        name="app_logout"
        ),
    url(r'^password_change$',
        views.password_change,
        {'post_change_redirect': 'datalocker:password_change_done'},
        name="password_change"
        ),
    url(r'^password_change_done$',
        views.password_change_done,
        name="password_change_done"
        ),
    url(r'^submission$',
        views.form_submission_view,
        name="form_submission"
        ),
    url(r'^users$',
        views.users_list,
        name='users_list'
        ),
    url(r'^(?P<locker_id>[0-9]+)/archive$',
        views.locker_archive,
        name='locker_archive'
        ),
    url(r'^(?P<locker_id>[0-9]+)/modify$',
        views.modify_locker,
        name='modify_locker'
        ),
    url(r'^(?P<locker_id>[0-9]+)/unarchive$',
        views.locker_unarchive,
        name='locker_unarchive'
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/add$',
        views.submission_add,
        name='submission_add'
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<submission_id>[0-9]+)/delete$',
        views.submission_delete,
        name='submission_delete'
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<submission_id>[0-9]+)/discussion/add$',
        views.comment_add,
        name='comment_add',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<submission_id>[0-9]+)/discussion/modify$',
        views.comment_modify,
        name='comment_modify',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<submission_id>[0-9]+)/discussion$',
        views.comments_list,
        name='comments_list',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<submission_id>[0-9]+)/undelete$',
        views.submission_undelete,
        name='submission_undelete'
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<submission_id>[0-9]+)/workflow/modify$',
        views.workflow_modify,
        name='workflow_modify',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<submission_id>[0-9]+)$',
    	views.submission_view,
    	name='submission_view'
    	),
    url(r'^(?P<locker_id>[0-9]+)/submissions$',
        views.submissions_list_view,
        name='submissions_list',
        ),
    url(r'^(?P<locker_id>[0-9]+)/users$',
        views.locker_users,
        name='locker_users'
        ),
    url(r'^(?P<locker_id>[0-9]+)/users/add$',
        views.locker_user_add,
        name='locker_user_add'
        ),
    url(r'^(?P<locker_id>[0-9]+)/users/delete$',
        views.locker_user_delete,
        name='locker_user_delete'
        ),
    )

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^testing/400$',
            views.testing_bad_request_view,
            name='testing_bad_request',
            ),
        url(r'^testing/403$',
            views.testing_forbidden_view,
            name='testing_forbidden',
            ),
        url(r'^testing/404$',
            views.testing_not_found_view,
            name='testing_not_found',
            ),
        url(r'^testing/500$',
            views.testing_server_error_view,
            name='testing_server_error',
            ),
        )

##
# EXAMPLE Urls
#
# /datalocker
# /datalocker/#/submissions
# /datalocker/#/submissions/#/view
# /datalocker/#/settings
# /datalocker/#/submissions/#/comments
