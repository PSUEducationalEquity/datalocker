
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
<<<<<<< HEAD
        return #Locker.objects.has_access()
              

class SubmissionView(generic.ListView):
    model = Submission
    template_name = 'datalocker/submission.html'
>>>>>>> 6a42f6c10021851f3f5c62dbab1632720ea682ff
