###Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response , get_object_or_404
from django.views import generic
from django.views.generic import View
from django.db.models.query import QuerySet
from django.db.models import Max
from django.forms.models import model_to_dict
from django.utils.text import slugify
from django.core.mail.message import EmailMessage
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context

from .models import Locker, Submission, LockerManager, LockerSetting, LockerQuerySet, User

import datetime, json, requests


public_fields = ['id', 'email', 'first_name', 'last_name']
from_email = 'eeqsys@psu.edu'
site_url = 'http://10.18.55.20:8000/datalocker/'


class LockerListView(generic.ListView):
    context_object_name = 'my_lockers_list'
    template_name = 'datalocker/index.html'


    def get_queryset(self):
        # Return all lockers for the current user
        return Locker.objects.active().has_access(self.request.user).annotate(latest_submission= Max('submissions__timestamp')).order_by('name')




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
        for submission in self.locker.submissions.all().order_by('-timestamp'):
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




class SubmissionAPIView(View):
    # currently adds a locker with the following inputs:
    # form_identifier of 'identifier'
    # form_url of 'url'
    # name of 'name'
    # owner of 'owner'
    # all values are dummy values, we need to pull the values off of the web form
    # creation
    def create_locker(identifier, name, url, owner):
        locker, created = Locker.objects.get_or_create(
            form_identifier=identifier,
            defaults={
                'name':name,
                'form_url':url,
                'owner': owner,
            }
        )
        return locker

    locker = []
    url = 'http://cookie.jsontest.com/'
    response = requests.get(url)
    data = response.json()
    data = json.dumps(data)
    identifier = "4051"
    owner = "das66"
    users = []
    name = "Python Created Locker"
    address = User.objects.get(username=owner)
    email = address.email
    submission = Submission()

    try:
        exists = Locker.objects.get(form_identifier=identifier)
        archived = Locker.objects.get(form_identifier=identifier).archive_timestamp
        if exists and archived != None:
            identifier += '-active'
            create_locker(identifier, name, url, owner)
            submission.locker = Locker.objects.get(form_identifier=identifier)
            lockerid = Locker.objects.get(form_identifier=identifier).id
            record = Submission.objects.all().order_by('-id')[0]
            site_url += str(lockerid) + '/submissions/' + str(record.id) + '/view'
            subject = 'New Form Submission Recevied'
            message = 'There was a recent submission to the ' + name + '\nView your new submissions at ' + site_url
        elif exists and archived == None:
            create_locker(identifier, name, url, owner)
            submission.locker = Locker.objects.get(form_identifier=identifier)
            lockerid = Locker.objects.get(form_identifier=identifier).id
            record = Submission.objects.all().order_by('-id')[0]
            site_url += str(lockerid) + '/submissions/' + str(record.id) + '/view'
            subject = 'New Form Submission Recevied'
            message = 'There was a recent submission to the ' + name + '\nView your new submissions at ' + site_url
    except:
        create_locker(identifier, name, url, owner)
        submission.locker = Locker.objects.get(form_identifier=identifier)
        lockerid = Locker.objects.get(form_identifier=identifier).id
        record = Submission.objects.all().order_by('-id')[0]
        site_url += str(lockerid) + '/submissions/' + str(record.id) + '/view'
        subject = 'New Locker Created'
        message = 'A new locker ' + name + ' was created due to a new form submission \nView your new submissions at ' + site_url
    submission.data=data
    submission.save()

    # code to send an email to the above address
    # Uncomment to send and receive the emails, tired of getting hundreds of emails
    send_mail(
        subject,
        message,
        from_email,
        [email],
    )




class SubmissionView(generic.DetailView):
    template_name = 'datalocker/submission_view.html'
    model = Submission


    def get_context_data(self, **kwargs):
        context = super(SubmissionView, self).get_context_data(**kwargs)
        context['oldest_disabled'] = True if self.object.id == self.object.oldest() else False
        context['older_disabled'] = True if self.object.id == self.object.older() else False
        context['newer_disabled'] = True if self.object.id == self.object.newer() else False
        context['newest_disabled'] = True if self.object.id == self.object.newest() else False
        return context



def locker_users(request, locker_id):
    if request.is_ajax():
        locker = get_object_or_404(Locker, pk=locker_id)
        users = []
        for user in locker.users.all():
            user_dict = {}
            for key, value in model_to_dict(user).iteritems():
                if key in public_fields:
                    user_dict[key] = value
            users.append(user_dict)
        return JsonResponse({'users': users})
    else:
        return HttpResponseRedirect(reverse('index'))




class LockerUserAdd(View):


    def post(self, *args, **kwargs):
        user = get_object_or_404(User, email=self.request.POST.get('email', ''))
        locker =  get_object_or_404(Locker, id=kwargs['locker_id'])
        if not user in locker.users.all():
            locker.users.add(user)
            locker.save()
        user_dict = {}
        for key,value in model_to_dict(user).iteritems():
            if key in public_fields:
                user_dict[key] = value
        name = Locker.objects.get(id=kwargs['locker_id'])
        subject = 'Granted Locker Access'
        site_url = 'http://10.18.55.20:8000/datalocker/'
        site_url += str(kwargs['locker_id']) + '/submissions'
        to = self.request.POST.get('email', "")
        body= 'Hello, '+ to +'\n'+' You now have access to a locker ' +  name.name +  '\n'+'You may click here to view it: ' + site_url
        email = EmailMessage(subject,
           body,
           from_email,
           [to])
        email.send()
        return JsonResponse(user_dict)



class LockerUserDelete(View):


    def post(self , *args, **kwargs):
        user = get_object_or_404(User, id=self.request.POST.get('id', ''))
        locker =  get_object_or_404(Locker, id=kwargs['locker_id'])
        if user in locker.users.all():
            locker.users.remove(user)
            locker.save()
        return JsonResponse({'user_id': user.id})




def archive_locker(request, **kwargs):
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    owner = Locker.objects.get(id=kwargs['locker_id']).owner
    locker.archive_timestamp = datetime.datetime.now()
    locker.save()
    subject = 'Locker Has Been Archived'
    message = "One of your lockers has been archived. The locker that has been archived is " + str(locker.name) + " and it was archived at " + str(locker.archive_timestamp)
    address = User.objects.get(username=owner)
    email = address.email
    send_mail(
        subject,
        message,
        from_email,
        [email],
    )
    if request.is_ajax():
        return JsonResponse({})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))


def modify_locker(request, **kwargs):
    locker =  get_object_or_404(Locker, id=kwargs['locker_id'])
    locker_name = locker.name
    locker_owner = locker.owner
    if request.method == 'POST':
        new_locker_name = request.POST.get('edit-locker')
        new_owner = request.POST.get('edit-owner')
        if new_locker_name != "":
             locker.name = new_locker_name
             locker.save()
        if new_owner != "":
            user = User.objects.get(email=new_owner).username
            locker.owner = user
            locker.save()
    return HttpResponseRedirect(reverse('datalocker:index'))


def unarchive_locker(request, **kwargs):
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    owner = Locker.objects.get(id=kwargs['locker_id']).owner
    if request.method == 'POST':
        locker.archive_timestamp = None
        locker.save()
    subject = 'Locker Has Been Unarchived'
    message = "One of your lockers has been archived. The locker that has been archived is " + locker.name
    address = User.objects.get(username=owner)
    email = address.email
    send_mail(
        subject,
        message,
        from_email,
        [email],
    )
    return HttpResponseRedirect(reverse('datalocker:index'))



