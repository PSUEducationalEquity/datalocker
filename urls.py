from django.conf.urls import patterns, url
from datalocker import views

urlpatterns = patterns('',
    url(r'^$', views.LockerView.as_view(), name='index'),
    url(r'listing', views.SubmissionListView.as_view(), name='listing'),
    url(r'submission', views.SubmissionView.as_view(), name='submission'),
)
