
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.views import generic
from django.views.generic import View
from django.db.models.query import QuerySet
from django.db.models import Max
from django.utils.text import slugify

from .models import Locker, Submission, LockerManager, LockerSetting, LockerQuerySet

import json


public_fields = 'id', 'email','locker' 

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
        self.locker = Locker.objects.get(pk=self.kwargs['locker_id'])
        context['locker'] = self.locker
        self.fields_list = self.locker.get_all_fields_list()
        context['fields_list'] = self.fields_list
        self.selected_fields = self.locker.get_selected_fields_list()
        context['selected_fields'] = self.selected_fields
        context['column_headings'] = ['Submitted Date', ] + self.selected_fields
        context['data'] = []
        for submission in self.locker.submissions.all():
            entry = [submission.id, submission.timestamp, ]
            for field, value in submission.data_dict().iteritems():
                if field in self.selected_fields:
                    entry.append(value)
            context['data'].append(entry)
        return context


    def get_queryset(self):
         # Return all submissions for selected locker
        return Submission.objects.filter(locker_id=self.kwargs['locker_id']).order_by('-timestamp')


    def post(self, *args, **kwargs):
        locker = Locker.objects.get(pk=self.kwargs['locker_id'])
        selected_fields = []
        for field in locker.get_all_fields_list():
            if slugify(field) in self.request.POST:
                selected_fields.append(field)
        selected_fields_setting, created = LockerSetting.objects.get_or_create(
            category='fields-list',
            setting_identifier='selected-fields',
            locker=locker,
            defaults={
                'setting': 'User-defined list of fields to display in tabular view',
                }
            )
        selected_fields_setting.value = json.dumps(selected_fields)
        selected_fields_setting.save()
        return HttpResponseRedirect(reverse('datalocker:submissions_list', kwargs={'locker_id': self.kwargs['locker_id']}))




class SubmissionView(generic.DetailView):
    template_name = 'datalocker/submission_view.html'
    model = Submission


    def get_context_data(self, **kwargs):
        context = super(SubmissionView, self).get_context_data(**kwargs)
        return context




#class LockerUserAdd(View):
    

    #def post(self, *args, **kwargs)
    #    user = get_object_or_404(User, id=kwargs['locker_id'])
    #    locker =  get_object_or_404(Locker, id=kwargs['locker_id'])
    #    user = Locker.objects.get(User, id=kwargs['locker_id'])
    #    user = []
    #    locker = Locker.objects.get(Locker, id=kwargs['locker_id'])
    #    for key, value in user:
    #       if something:
    #           key.model_to_dict().iteritems()
    #    Locker.user.add()
    #    Locker.save()
    #    name = Locker.objects.get(id=kwargs['locker_id'])
    #    subject = 'Locker Access'
    #    from_email = 'eeqsys@psu.edu'
    #    to = self.request.POST.get('email', "")_
    #    body= 'Hello,\nYou now have access to a locker' +' '+ name.name
    #    email = EmailMessage(subject, 
    #            body, 
    #            from_email,
    #            [to])                        
    #    email.send()
    #    Locker.user.add()
    #    Locker.save()
    #return jsonResponse()


    


#class LockerUserDelete(view):
    

    # def post(self, *args, **kwargs)
    #    user =  get_object_or_404(User, id=kwargs['locker_id'])
    #    locker =  get_object_or_404(Locker, id=kwargs['locker_id'])
    #    Locker.user.remove()
    #    return HttpResponseRedirect(reverse('datalocker:index', kwargs={'locker_id': self.kwargs['locker_id']}))