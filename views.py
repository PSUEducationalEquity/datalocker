
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




class SubmissionView(generic.DetailView):
    template_name = 'datalocker/submission_view.html'
    model = Submission


    def get_context_data(self, **kwargs):
        context = super(SubmissionView, self).get_context_data(**kwargs)
        return context



class LockerSubmissionView(generic.ListView):
    context_object_name = 'my_submission_list'
    template_name = 'datalocker/submission_list.html'


    def get_context_data(self, **kwargs):
        context = super(LockerSubmissionView, self).get_context_data(**kwargs)
        context['locker'] = Locker.objects.get(pk=self.kwargs['locker_id'])
        return context


    def get_queryset(self):
         # Return all submissions for selected locker
        return Submission.objects.filter(locker_id=self.kwargs['locker_id']).order_by('-timestamp')

