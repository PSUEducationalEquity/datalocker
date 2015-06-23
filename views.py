
from django.shortcuts import render
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
        #user =
        return #Locker.objects.has_access(user)


class SubmissionView(generic.ListView):
    model = Submission
    template_name = 'datalocker/submission.html'
