
from django.shortcuts import render, render_to_response
from django.views import generic
from .models import Locker, LockerManager, LockerSettings, LockerUser, Submission


# def index(request):
#     """
#     Displays the application home page
#     """
#     return render(request, 'datalocker/index.html', {})


class LockerView(generic.ListView):
    model = Locker
    template_name = 'datalocker/index.html'


    def get_queryset(self):
        # Return all lockers for the current user
        return #Locker.objects.has_access(self)



class SubmissionView(generic.ListView):
    model = Submission
    template_name = 'datalocker/submission.html'


class SubmissionListView(generic.ListView):
    model = Submission
    template_name = 'datalocker/listing.html'


    def get_queryset(self):
        return Submission.objects.all()