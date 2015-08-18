### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
from django.db.models import Max
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response , get_object_or_404
from django.template.loader import get_template
from django.template import Context
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import View

from .decorators import user_has_locker_access
from .models import Locker, LockerManager, LockerSetting, LockerQuerySet, Submission

import datetime, json, logging, requests


logger = logging.getLogger(__name__)


##
## Helper Functions
##

def _get_notification_from_address(email_purpose):
    """
    Gets the from address for notification emails from settings.py. If the
    setting does not exist or is blank, it logs the error and uses
    `email_purpose` to explain what email was trying to be sent.
    """
    from_addr = ''
    try:
        from_addr = settings.NOTIFICATIONS_FROM
    except:
        logger.warning("The '%s' email was not sent because " \
            "NOTIFICATIONS_FROM was not defined in settings_local.py or " \
            "settings.py" % email_purpose)
    else:
        if from_addr == '':
            logger.warning("The '%s' email was not sent because " \
                "NOTIFICATIONS_FROM in settings_local.py or settings.py " \
                "is blank" % email_purpose)
    return from_addr


def _get_public_user_dict(user):
    """
    Converts a user object to a dictionary and only returns certain
    publically-available fields for the user.
    """
    public_fields = ['id', 'email', 'first_name', 'last_name']
    user_dict = {}
    for key, value in model_to_dict(user).iteritems():
        if key in public_fields:
            user_dict[key] = value
    return user_dict





##
## Views
##

def archive_locker(request, **kwargs):
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    owner = locker.owner
    locker.archive_timestamp = timezone.now()
    locker.save()
    if request.is_ajax():
        return JsonResponse({})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))




def custom_404(request):
    response = render_to_response('404.html')
    response.status_code = 404
    return response




def delete_submission(request, **kwargs):
    submission = get_object_or_404(Submission, id=kwargs['pk'])
    submission.deleted = timezone.now()
    submission.save()
    if request.is_ajax():
        return JsonResponse({
            'id': submission.id,
            'timestamp': submission.timestamp,
            })
    else:
        return HttpResponseRedirect(reverse('datalocker:submission_list',
            kwargs={'id': self.kwargs['id']}))




@csrf_exempt
def form_submission_view(request, **kwargs):
    """
    Handles form submissions from outside applications to be saved in lockers.
    """
    # redirect non-form submissions to the main page
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('datalocker:index'))

    safe_values = {
        'identifier': request.POST.get('form-id', ''),
        'name': request.POST.get('name', 'New Locker'),
        'url': request.POST.get('url', ''),
        'owner': request.POST.get('owner', ''),
        'data': request.POST.get('data', ''),
        }
    try:
        locker = Locker.objects.filter(
            form_identifier=safe_values['identifier'],
            archive_timestamp=None,
            ).order_by('-pk')[0]
    except (Locker.DoesNotExist, IndexError):
        locker = Locker(
            form_identifier=safe_values['identifier'],
            name=safe_values['name'],
            form_url=safe_values['url'],
            owner=safe_values['owner'],
            )
        locker.save()
    submission = Submission(
        locker = locker,
        data = safe_values['data'],
        )
    submission.save()

    try:
        address = User.objects.get(username=safe_values['owner']).email
    except User.DoesNotExist:
        logger.info("New submission saved to orphaned locker: %s" % (
            reverse(
                'datalocker:submissions_view',
                kwargs={'locker_id': locker.id, 'pk': submission.id}
                ),
        ))
    else:
        from_addr = _get_notification_from_address("new submission")
        if from_addr:
            subject = "%s - new submission" % safe_values['name']
            message = "A new form submission was saved to the Data Locker. " \
                "The name of the locker and links to view the submission " \
                "are provided below.\n\n" \
                "Locker: %s\n\n" \
                "View submission: %s\n" \
                "View all submissions: %s\n" % (
                    request.POST.get('name', 'New Locker'),
                    request.build_absolute_uri(
                        reverse(
                            'datalocker:submissions_view',
                            kwargs={'locker_id': locker.id, 'pk': submission.id}
                            )
                        ),
                    request.build_absolute_uri(
                        reverse(
                            'datalocker:submissions_list',
                            kwargs={'locker_id': locker.id,}
                            )
                        ),
                    )
            try:
                send_mail(subject, message, from_addr, [address])
            except Exception, e:
                logger.exception("New submission email to the locker owner failed")
    return HttpResponse(status=201)




class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)



class UserHasLockerAccessMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(UserHasLockerAccessMixin, cls).as_view(**initkwargs)
        return user_has_locker_access(view)




class LockerListView(LoginRequiredMixin, generic.ListView):
    template_name = 'datalocker/index.html'
    model = Locker


    def get_context_data(self, **kwargs):
        """
        Accesses the logged in user and searched through all the lockers they
        have access to. It only returns the lockers that they have access to
        and don't own.
        """
        user = self.request.user
        context = super(LockerListView, self).get_context_data(**kwargs)
        context['shared'] = Locker.objects.active().has_access(
            self.request.user).annotate(latest_submission= Max(
                'submissions__timestamp')).order_by('name').exclude(
                    owner=user)
        context['owned'] = Locker.objects.active().has_access(
            self.request.user).annotate(latest_submission= Max(
                'submissions__timestamp')).order_by('name').filter(
                    owner=user)
        return context




class LockerSubmissionsListView(LoginRequiredMixin, generic.ListView):
    template_name = 'datalocker/submission_list.html'


    def get_context_data(self, **kwargs):
        context = super(LockerSubmissionsListView, self).get_context_data(**kwargs)
        locker = Locker.objects.get(pk=self.kwargs['locker_id'])
        context['locker'] = locker
        fields_list = locker.get_all_fields_list()
        context['fields_list'] = fields_list
        selected_fields = locker.get_selected_fields_list()
        context['selected_fields'] = selected_fields
        context['column_headings'] = ['Submitted Date', ] + selected_fields
        context['data'] = []
        for submission in locker.submissions.all().order_by('-timestamp'):
            entry = [submission.id, True if submission.deleted else False, submission.timestamp, ]
            for field, value in submission.data_dict().iteritems():
                if field in selected_fields:
                    entry.append(value)
            context['data'].append(entry)
        return context


    def get_queryset(self):
        """ Return all submissions for selected locker """
        return Submission.objects.filter(
            locker_id=self.kwargs['locker_id']).order_by('-timestamp')


    def post(self, *args, **kwargs):
        """
        Takes the checkboxes selected on the select fields dialog and saves
        those as a selected-fields setting which is loaded then on every page
        load thereafter.
        """
        locker = Locker.objects.get(pk=self.kwargs['locker_id'])
        locker.save_selected_fields_list(self.request.POST)
        return HttpResponseRedirect(reverse('datalocker:submissions_list',
            kwargs={'locker_id': self.kwargs['locker_id']}))




def locker_users(request, locker_id):
    if request.is_ajax():
        locker = get_object_or_404(Locker, pk=locker_id)
        users = []
        for user in locker.users.all():
            users.append(_get_public_user_dict(user))
        return JsonResponse({'users': users})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))




class LockerUserAdd(View):
    def post(self, *args, **kwargs):
        user = get_object_or_404(User, email=self.request.POST.get('email', ''))
        locker =  get_object_or_404(Locker, id=kwargs['locker_id'])
        if not user in locker.users.all():
            locker.users.add(user)
            locker.save()
        from_addr = _get_notification_from_address("locker access granted")
        if from_addr:
            subject = "Access to Locker: %s" % locker.name
            to_addr = self.request.POST.get('email', '')
            message = "The following Data Locker of form submissions has been " \
                "shared with you.\n\n" \
                "Locker: %s\n\n" \
                "You can view the submissions at:\n%s\n" % (
                    locker.name,
                    request.build_absolute_uri(
                        reverse(
                            'datalocker:submissions_list',
                            kwargs={'locker_id': locker.id,}
                            )
                        ),
                    )
            try:
                send_mail(subject, message, from_addr, [to_addr])
            except:
                logger.exception("Locker shared with you email failed to send")
        return JsonResponse(_get_public_user_dict(user))




class LockerUserDelete(View):
    def post(self , *args, **kwargs):
        user = get_object_or_404(User, id=self.request.POST.get('id', ''))
        locker =  get_object_or_404(Locker, id=kwargs['locker_id'])
        if user in locker.users.all():
            locker.users.remove(user)
            locker.save()
        return JsonResponse({'user_id': user.id})




class SubmissionView(LoginRequiredMixin, generic.DetailView):
    template_name = 'datalocker/submission_view.html'
    model = Submission


    def get_context_data(self, **kwargs):
        context = super(SubmissionView, self).get_context_data(**kwargs)
        context['oldest_disabled'] = True if self.object.id == self.object.oldest() else False
        context['older_disabled'] = True if self.object.id == self.object.older() else False
        context['newer_disabled'] = True if self.object.id == self.object.newer() else False
        context['newest_disabled'] = True if self.object.id == self.object.newest() else False
        return context




@require_http_methods(["POST"])
def modify_locker(request, **kwargs):
    locker =  get_object_or_404(Locker, id=kwargs['locker_id'])
    previous_owner = locker.owner
    new_locker_name = request.POST.get('edit-locker', '')
    new_owner_email = request.POST.get('edit-owner', '')
    if new_locker_name:
        locker.name = new_locker_name
    if new_owner_email:
        try:
            new_owner = User.objects.get(email=new_owner_email).username
        except User.DoesNotExist:
            logger.error(
                "Attempted to reassign locker (%s) to non-existent user (%s)" %
                (locker.name, new_owner)
                )
            ### TODO: Report this problem back to the end user
        else:
            locker.owner = new_owner
            from_addr = _get_notification_from_address("change locker owner")
            if from_addr:
                subject = "Ownership of Locker: %s" % locker.name
                to_addr = self.request.POST.get('email', '')
                message = "%s %s has changed the ownership of the following " \
                    "Data Locker of form submissions to you.\n\n" \
                    "Locker: %s\n\n" \
                    "You can view the submissions at:\n%s\n" % (
                        previous_owner.first_name,
                        previous_owner.last_name,
                        locker.name,
                        request.build_absolute_uri(
                            reverse(
                                'datalocker:submissions_list',
                                kwargs={'locker_id': locker.id,}
                                )
                            ),
                        )
                try:
                    send_mail(subject, message, from_addr, [to_addr])
                except:
                    logger.exception("Locker ownership changed to you email failed to send")
    locker.save()
    return HttpResponseRedirect(reverse('datalocker:index'))




def unarchive_locker(request, **kwargs):
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    owner = locker.owner
    locker.archive_timestamp = None
    locker.save()
    return HttpResponseRedirect(reverse('datalocker:index'))




def undelete_submission(request, **kwargs):
    submission = get_object_or_404(Submission, id=kwargs['pk'])
    submission.deleted = None
    submission.save()
    if request.is_ajax():
        return JsonResponse({
            'id': submission.id,
            'timestamp': submission.timestamp,
            })
    else:
        return HttpResponseRedirect(reverse('datalocker:submission_list'))
