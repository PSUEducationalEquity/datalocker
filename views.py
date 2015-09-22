### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
from django.db.models import Max
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template.loader import get_template
from django.template import Context
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import View

from .decorators import user_has_locker_access
from .helpers import UserColorHelper
from .models import Comment, Locker, LockerManager, LockerSetting, \
    LockerQuerySet, Submission

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



def _get_public_comment_dict(request, comment):
    public_fields = ['comment', 'submission', 'user', 'id', 'parent_comment', 'color']
    comment_dict = {}
    submission = comment.submission
    locker = Locker.objects.get(submissions=submission)
    for key, value in model_to_dict(comment).iteritems():
        if key in public_fields:
            if key == 'user':
                name = User.objects.get(id=value).username
                comment_dict[key] = name
                try:
                    if not request.session.get(name + '-color', None):
                        color_mapping = _user_color_lookup(request, locker)
                        request.session[name + '-color'] = color_mapping[name]
                        comment_dict['color'] = request.session[name + '-color']
                    else:
                        comment_dict['color'] = request.session[name + '-color']
                except KeyError:
                    comment_dict['color'] = ''
            else:
                comment_dict[key] = value
    return comment_dict




def _user_color_lookup(request, locker):
    colors = UserColorHelper()
    avail_colors = colors.list_of_available_colors()
    users = {}
    try:
        users[locker.owner] = avail_colors.pop()
    except Exception:
        pass
    for user in locker.users.all():
        try:
            color = avail_colors.pop()
        except Exception:
            return ''
        users[user.username] = color
    return users




##
## Views
##



@require_http_methods(["POST"])
def add_comment(request, **kwargs):
    submission = get_object_or_404(Submission, id=kwargs['pk'])
    user_comment = request.POST.get('comment', '')
    comment = Comment(
        submission=submission,
        comment=user_comment,
        user=request.user,
        timestamp=timezone.now(),
        )
    comment.save()
    if not request.session.get(request.user.username + '-color', None):
        locker = Locker.objects.get(id=kwargs['locker_id'])
        color_mapping = _user_color_lookup(request, locker)
        request.session[request.user.username + '-color'] = color_mapping[request.user.username]
    return JsonResponse({
        'comment': user_comment,
        'submission': submission.id,
        'user': request.user.username,
        'id': comment.id,
        'color': request.session[request.user.username + '-color']
        })




@require_http_methods(["POST"])
def edit_comment(request, **kwargs):
    submission = get_object_or_404(Submission, id=kwargs['pk'])
    user_comment = request.POST.get('comment', '')
    comment = Comment.objects.get(
        id=request.POST.get('id'),
        )
    if Comment.is_editable(comment):
        comment.comment = user_comment
        comment.save()
    return JsonResponse({
        'comment': user_comment,
        'submission': submission.id,
        'user': request.user.username,
        'id': comment.id,
        })




@require_http_methods(["POST"])
def add_reply(request, **kwargs):
    submission = get_object_or_404(Submission, id=kwargs['pk'])
    parent_comment = get_object_or_404(Comment, id=request.POST['parent_comment'])
    user_comment = request.POST.get('comment', '')
    comment = Comment(
        submission=submission,
        comment=user_comment,
        user=request.user,
        timestamp=timezone.now(),
        parent_comment=parent_comment,
        )
    comment.save()
    if not request.session.get(request.user.username + '-color', None):
        locker = Locker.objects.get(id=kwargs['locker_id'])
        color_mapping = _user_color_lookup(request, locker)
        request.session[request.user.username + '-color'] = color_mapping[request.user.username]
    return JsonResponse({
        'comment': user_comment,
        'submission': submission.id,
        'user': request.user.username,
        'id': comment.id,
        'parent_comment': parent_comment.id,
        'color': request.session[request.user.username + '-color']
        })




def archive_locker(request, **kwargs):
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    owner = locker.owner
    locker.archive_timestamp = timezone.now()
    locker.save()
    if request.is_ajax():
        return JsonResponse({})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))




@require_http_methods(["POST"])
def change_workflow_state(request, **kwargs):
    submission = Submission.objects.get(id=kwargs['pk'])
    new_state = request.POST.get('workflow_state_update', '')
    submission.workflow_state = new_state
    submission.save()
    return JsonResponse({
        'new state': new_state
        })



def custom_404(request):
    response = render_to_response('datalocker/404.html')
    response.status_code = 404
    return response


@login_required()
@require_http_methods(["POST"])
def delete_submission(request, **kwargs):
    """
    Marks a submission as deleted in the database.
    """
    if request.is_ajax():
        submission = get_object_or_404(Submission, id=kwargs['pk'])
        submission.deleted = timezone.now()
        submission.save()
        purge_timestamp = submission.deleted + datetime.timedelta(
            days=settings.SUBMISSION_PURGE_DAYS
            )
        return JsonResponse({
            'id': submission.id,
            'timestamp': submission.timestamp,
            'deleted': submission.deleted,
            'purge_timestamp': purge_timestamp,
            })
    else:
        return HttpResponseRedirect(reverse(
            'datalocker:submission_list',
            kwargs={
                'id': self.kwargs['id'],
                'deleted': submission.deleted
                }
            ))


@csrf_exempt
def form_submission_view(request, **kwargs):
    """
    Handles form submissions from outside applications to be saved in lockers.
    """
    # redirect non-form submissions to the main page
    if request.method != 'POST':
        return HttpResponseRedirect(reverse('datalocker:index'))

    safe_values = {
        'identifier': request.POST.get('form-id', '').strip(),
        'name': request.POST.get('name', 'New Locker').strip(),
        'url': request.POST.get('url', '').strip(),
        'owner': request.POST.get('owner', '').strip(),
        'data': request.POST.get('data', '').strip(),
        }
    try:
        locker = Locker.objects.filter(
            form_identifier=safe_values['identifier'],
            archive_timestamp=None,
            ).order_by('-pk')[0]
        created = False
    except (Locker.DoesNotExist, IndexError):
        locker = Locker(
            form_identifier=safe_values['identifier'],
            name=safe_values['name'],
            form_url=safe_values['url'],
            owner=safe_values['owner'],
            )
        locker.save()
        created = True
    submission = Submission(
        locker = locker,
        data = safe_values['data'],
        )
    submission.save()
    logger.info("New submission (%s) from %s saved to %s locker (%s)" % (
        submission.pk,
        safe_values['url'],
        'new' if created else 'existing',
        locker.pk
        ))

    try:
        address = []
        address.append(User.objects.get(username=safe_values['owner']).email)
        try:
            if Locker.shared_users_receive_email(locker):
                for user in locker.users.all(): address.append(user.email)
        except Exception:
            logger.warning("No setting saved")
    except User.DoesNotExist:
        logger.warning("New submission saved to orphaned locker: %s" % (
            reverse(
                'datalocker:submission_view',
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
                            'datalocker:submission_view',
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
                for to_email in address:
                    send_mail(subject, message, from_addr, [to_email])
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



@login_required()
def locker_list_view(request):
    """
    Returns a list of lockers owned by the current user and a list of those
    lockers shared with the current user.
    """
    shared_lockers = Locker.objects.active().has_access(
        request.user
    ).annotate(
        latest_submission= Max('submissions__timestamp')
    ).order_by('name').exclude(owner=request.user)
    my_lockers = Locker.objects.active().has_access(
        request.user
    ).annotate(
        latest_submission= Max('submissions__timestamp')
    ).order_by('name').filter(owner=request.user)
    return render(request, 'datalocker/index.html', {
        'shared': shared_lockers,
        'owned': my_lockers,
        })



class LockerSubmissionsListView(LoginRequiredMixin, UserHasLockerAccessMixin, generic.ListView):
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
        context['purge_days'] = settings.SUBMISSION_PURGE_DAYS

        # build the list of submissions to be displayed
        context['data'] = []
        for submission in locker.submissions.all().order_by('-timestamp'):
            if submission.deleted is not None:
                purge_date = submission.deleted + datetime.timedelta(
                    days=settings.SUBMISSION_PURGE_DAYS
                    )
            else:
                purge_date = None
            # the first 4 elements are fixed values
            entry = [
                submission.id,
                True if submission.deleted else False,
                purge_date,
                submission.timestamp,
                ]
            # the remaining elements are based on the user-selected fields
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




def get_comments_view(request, **kwargs):
    locker = Locker.objects.get(id=kwargs['locker_id'])
    if Locker.get_settings(locker):
        if request.is_ajax():
            # If statement to make sure the user should be able to see the comments
            all_comments = Comment.objects.filter(submission=kwargs['pk'], parent_comment=None)
            all_replies = Comment.objects.filter(submission=kwargs['pk']
                ).exclude(parent_comment=None)
            comments = []
            replies = []
            for comment in all_comments:
                comments.append(_get_public_comment_dict(request, comment))
            for comment in all_replies:
                replies.append(_get_public_comment_dict(request, comment))
            return JsonResponse(
                {
                'comments': comments,
                'replies': replies,
                })
        else:
            return HttpResponseRedirect(reverse('datalocker:submission_view',
         kwargs={'locker_id': locker.id, 'pk': pk}))
    else:
        pk = Submission.objects.get(id=kwargs['pk'])
        return HttpResponseRedirect(reverse('datalocker:submission_view',
         kwargs={'locker_id': locker.id, 'pk': pk}))



@login_required()
@require_http_methods(["POST"])
def locker_user_add(request, locker_id):
    """
    Adds the indicated user to the locker's list of users
    """
    if request.is_ajax():
        user = get_object_or_404(User, email=request.POST.get('email', ''))
        locker =  get_object_or_404(Locker, id=locker_id)
        if not user in locker.users.all():
            locker.users.add(user)
            locker.save()
            from_addr = _get_notification_from_address("locker access granted")
            if from_addr:
                subject = "Access to Locker: %s" % locker.name
                to_addr = user.email
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
        return JsonResponse({ 'user': _get_public_user_dict(user) })
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))


@login_required()
@require_http_methods(["POST"])
def locker_user_delete(request, locker_id):
    """
    Removes the indicated user from the locker's list of users
    """
    if request.is_ajax():
        user = get_object_or_404(User, id=request.POST.get('id', ''))
        locker =  get_object_or_404(Locker, id=locker_id)
        if user in locker.users.all():
            locker.users.remove(user)
            locker.save()
        return JsonResponse({'user_id': user.id})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))


@login_required()
@require_http_methods(["GET", "HEAD"])
def locker_users(request, locker_id):
    if request.is_ajax():
        locker = get_object_or_404(Locker, pk=locker_id)
        users = []
        for user in locker.users.all():
            users.append(_get_public_user_dict(user))
        return JsonResponse({'users': users})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))




@require_http_methods(["POST"])
def modify_locker(request, **kwargs):
    """
    Modifies locker name, ownership, and settings.
    """
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    try:
        previous_owner = User.objects.get(username=locker.owner)
    except User.DoesNotExist:
        previous_owner = request.user
    new_locker_name = request.POST.get('locker-name', '')
    new_owner_email = request.POST.get('locker-owner', '')
    if new_locker_name != "":
        locker.name = new_locker_name
    if new_owner_email != "":
        try:
            new_owner = User.objects.get(email=new_owner_email).username
        except User.DoesNotExist:
            logger.error(
                "Attempted to reassign locker (%s) to non-existent user (%s)" %
                (locker.name, new_owner_email)
                )
            messages.error(
                request,
                "<strong>Oops!</strong> The user (%s) you tryed to make the " \
                "owner of the <strong>%s</strong> locker does not exist. " \
                "<strong>You still own the locker.</strong>" % (
                    new_owner_email,
                    locker.name
                    ))
        else:
            locker.owner = new_owner
            from_addr = _get_notification_from_address("change locker owner")
            if from_addr:
                subject = "Ownership of Locker: %s" % locker.name
                to_addr = new_owner_email
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
                    logger.exception("Locker ownership changed to you email " \
                        "failed to send")
    locker.save()

    # update the locker settings
    locker.shared_users_notification(
        bool(request.POST.get('shared-users', False))
    )
    locker.workflow_enabled(
        bool(request.POST.get('workflow-enable', False))
    )
    locker.workflow_users_can_edit(
        bool(request.POST.get('workflow-users-can-edit', False))
    )
    locker.workflow_states(request.POST.get('workflow-states', ''))
    locker.discussion_enabled(
        bool(request.POST.get('discussion-enable', False))
    )
    locker.discussion_users_have_access(
        bool(request.POST.get('discussion-users-have-access', False))
    )
    return HttpResponseRedirect(reverse('datalocker:index'))




@login_required()
@require_http_methods(["GET", "HEAD"])
@user_has_locker_access()
def submission_view(request, **kwargs):
    """
    Displays an individual submission
    """
    submission = get_object_or_404(Submission, pk=pk)
    oldest = submission.objects.oldest(locker)
    older = submission.older()
    newer = submission.newer()
    newest = submission.objects.newest(locker)
    workflow_enabled = submission.locker.workflow_enabled()
    discussion_enabled = submission.locker.discussion_enabled()
    return render(request, 'datalocker/submission_view.html', {
        'submission': submission,

        'oldest': oldest,
        'older': older,
        'newer': newer,
        'newest': newest,
        'oldest_disabled': True if submission.id == oldest.id else False,
        'older_disabled': True if submission.id == older.id else False,
        'newer_disabled': True if submission.id == newer.id else False,
        'newest_disabled': True if submission.id == newest.id else False,

        'workflow_enabled': workflow_enabled,
        'workflow_users_can_edit': submission.locker.workflow_users_can_edit() or submission.locker.owner == self.request.user.username,
        'workflow_states': submission.locker.workflow_states(),
        'workflow_state': submission.workflow_state,

        'discussion_enabled': discussion_enabled,
        'discussion_users_have_access'] = submission.locker.discussion_users_have_access() or submission.locker.owner == self.request.user.username,

        'sidebar_enabled': workflow_enabled or discussion_enabled,
        })




def unarchive_locker(request, **kwargs):
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    owner = locker.owner
    locker.archive_timestamp = None
    locker.save()
    return HttpResponseRedirect(reverse('datalocker:index'))




@login_required()
@require_http_methods(["POST"])
def undelete_submission(request, **kwargs):
    """
    Removes the deleted timestamp from a submission
    """
    if request.is_ajax():
        submission = get_object_or_404(Submission, id=kwargs['pk'])
        submission.deleted = None
        submission.save()
        return JsonResponse({
            'id': submission.id,
            'timestamp': submission.timestamp,
            })
    else:
        return HttpResponseRedirect(reverse(
            'datalocker:submission_list',
            kwargs={
                'id': self.kwargs['id'],
                'deleted': submission.deleted
                }
            ))


@login_required()
@require_http_methods(["GET", "HEAD"])
def users_list(request, **kwargs):
    """
    Returns a list of all the user email addresses in the system
    """
    users_list = []
    for user in User.objects.all():
        users_list.append({
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            })
    return JsonResponse({ 'users': users_list })
