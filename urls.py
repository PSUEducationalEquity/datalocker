from django.conf.urls import patterns, url
from datalocker import views

urlpatterns = patterns('',
    url(r'^$', views.LockerView.as_view(), name='index'),

)
