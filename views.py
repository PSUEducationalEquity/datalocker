
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.views import generic
from django.db.models.query import QuerySet
from django.db.models import Max

from .models import Locker, Submission, LockerManager, LockerSetting, LockerQuerySet




class LockerListView(generic.ListView):
    context_object_name = 'my_lockers_list'
    template_name = 'datalocker/index.html'


    def get_queryset(self):
        # Return all lockers for the current user
        lastest_submission = Locker.objects.all()
        return Locker.objects.active().has_access(self.request.user).annotate(lastest_submission= Max('submissions__timestamp')).order_by('name')




class LockerSubmissionView(generic.ListView):
    template_name = 'datalocker/submission_list.html'


    def get_context_data(self, **kwargs):
        context = super(LockerSubmissionView, self).get_context_data(**kwargs)
        context['locker'] = Locker.objects.get(pk=self.kwargs['locker_id'])
        fields_list = []
        for submission in context['locker'].submissions.all():
            fields = submission.data_dict().keys()
            for field in fields:
                #if field[-1] == ':':
                #    field = field[:-1]
                if not field in fields_list:
                    fields_list.append(field)
            context['fields_list'] = fields_list
        selected_fields = context['fields_list']
        context['column_headings'] = ['Date', ] + selected_fields
        context['data'] = []
        for submission in context['locker'].submissions.all():
            entry = [submission.id, submission.timestamp, ]
            for field, value in submission.data_dict().iteritems():
                if field in selected_fields:
                    entry.append(value)
            context['data'].append(entry)
        return context


    def get_queryset(self):
         # Return all submissions for selected locker
        return Submission.objects.filter(locker_id=self.kwargs['locker_id']).order_by('-timestamp')


    def post(self, *args, **kwargs):

        return reverse('datalocker:submissions_list', kwargs={'locker_id': kwargs['locker_id']})






class SubmissionView(generic.DetailView):
    template_name = 'datalocker/submission_view.html'
    model = Submission


    def get_context_data(self, **kwargs):
        context = super(SubmissionView, self).get_context_data(**kwargs)
        return context
