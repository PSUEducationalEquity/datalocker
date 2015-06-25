from django.shortcuts import render, render_to_response
from django.views import generic
from django.db.models.query import QuerySet
from .models import Locker, Submission , LockerManager ,LockerQuerySet




class LockerListView(generic.ListView):
    context_object_name = 'my_lockers_list'
    template_name = 'datalocker/index.html'


   


    def get_queryset(self):
        # Return all lockers for the current user
        #return        
        return Locker.objects.active().has_access(self.request.user).order_by("name")




class SubmissionView(generic.ListView):
    context_object_name = 'submission_view'
    template_name = 'datalocker/submission_view.html'


    def get_queryset(self):
         # Return all submissions for selected locker
        data = Submission.objects.all()
        return data




class LockerSubmissionView(generic.ListView):
    context_object_name = 'my_submission_list'
    template_name = 'datalocker/submission_list.html'


    def get_queryset(self):
         # Return all submissions for selected locker

        data = Submission.objects.all().order_by('-timestamp')
        return data
