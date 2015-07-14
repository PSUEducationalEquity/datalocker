###Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###
from django.conf.urls import patterns, url
from datalocker import views

urlpatterns = patterns('',
    #url(r'^(?P<locker_id>[0-9]+)/locker/add$', views.LockerUserAdd.as_view(),
     #   name='index'),
    url(r'^$', views.LockerListView.as_view(), name='index'),
    url(r'^(?P<locker_id>[0-9]+)/submissions/(?P<pk>[0-9]+)/view$',
    	views.SubmissionView.as_view(
            context_object_name='submission_view'),
    	name='submissions_view'
    	),
    url(r'^(?P<locker_id>[0-9]+)/submissions$',
        views.LockerSubmissionView.as_view(
            context_object_name='my_submission_list'),
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

