###Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###

from django.conf.urls import patterns, url
from datalocker import views

urlpatterns = patterns('',
    url(r'^submission$',
        views.form_submission_view,
        name="form_submission"),
    url(r'^(?P<locker_id>[0-9]+)/archive$',
        views.archive_locker,
        name='archive_locker'),
    url(r'^(?P<locker_id>[0-9]+)/unarchive$',
        views.unarchive_locker,
        name='unarchive_locker'),
    url(r'^(?P<locker_id>[0-9]+)/modify$',
        views.modify_locker,
        name='modify_locker'),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<pk>[0-9]+)/delete_submission$',
        views.delete_submission,
        name='delete_submission'),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<pk>[0-9]+)/undelete_submission$',
        views.undelete_submission,
        name='undelete_submission'),
    url(r'^(?P<locker_id>[0-9]+)/users$',
        views.locker_users,
        name='locker_users'),
    url(r'^all_users$',
        views.get_all_users,
        name='get_all_users'),
    url(r'^(?P<locker_id>[0-9]+)/users/delete$',
        views.LockerUserDelete.as_view(),
        name='locker_user_delete'),
    url(r'^(?P<locker_id>[0-9]+)/users/add$',
        views.LockerUserAdd.as_view(),
        name='locker_user_add'),
    url(r'^$',
        views.locker_list_view,
        name='index',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<pk>[0-9]+)/view/workflow_state$',
        views.change_workflow_state,
        name='workflow_states',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<pk>[0-9]+)/view/comments/add$',
        views.add_comment,
        name='add_comment',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<pk>[0-9]+)/view/comments/addReply$',
        views.add_reply,
        name='add_reply',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<pk>[0-9]+)/view/comments/addEdit$',
        views.edit_comment,
        name='edit_comment',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<pk>[0-9]+)/view/comments$',
        views.get_comments_view,
        name='get_comments',
        ),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<pk>[0-9]+)/view$',
    	views.SubmissionView.as_view(context_object_name='submission_view'),
    	name='submissions_view'
    	),
    url(r'^(?P<locker_id>[0-9]+)/submissions$',
        views.LockerSubmissionsListView.as_view(context_object_name='my_submission_list'),
        name='submissions_list',
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
