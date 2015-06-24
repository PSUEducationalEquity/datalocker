from django.shortcuts import render, render_to_response
from django.views import generic

from .models import Locker, Submission


class LockerListView(generic.ListView):
    context_object_name = 'my_lockers_list'
    template_name = 'datalocker/index.html'


    def get_queryset(self):
        # Return all lockers for the current user
        return Locker.objects.has_access(self.request.user)



class SubmissionView(generic.ListView):
    model = Submission
    template_name = 'datalocker/submission.html'


class SubmissionListView(generic.ListView):
    model = Submission
    template_name = 'datalocker/listing.html'


    def get_queryset(self):
        return Submission.objects.all()