### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.mail import send_mail
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
from django.db.models import Max
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseBadRequest, \
    HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.template.loader import get_template
from django.template import Context
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views.generic import View

from .decorators import user_has_locker_access
from .helpers import UserColors
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
    public_fields = ['id', 'username', 'email', 'first_name', 'last_name']
    user_dict = {}
    for key, value in model_to_dict(user).iteritems():
        if key in public_fields:
            user_dict[key] = value
    return user_dict




##
## Mixins
##

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




##
## Views
##

@login_required
@require_http_methods(["POST"])
def archive_locker(request, **kwargs):
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    owner = locker.owner
    locker.archive_timestamp = timezone.now()
    locker.save()
    if request.is_ajax():
        return JsonResponse({})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))


def bad_request_view(request):
    """
    Displays a custom bad request (400) page
    """
    return render(request, 'datalocker/400.html', {})


@login_required
@require_http_methods(["POST"])
def comment_add(request, locker_id, submission_id):
    """
    Adds a comment or reply to the specified submission
    """
    submission = get_object_or_404(Submission, id=submission_id)
    comment_text = request.POST.get('comment', '').strip()
    parent_id = request.POST.get('parent', None)
    if parent_id:
        try:
            parent = Comment.objects.get(pk=parent_id)
        except Comment.DoesNotExist:
            parent = None
    else:
        parent = None
    if comment_text:
        comment = Comment(
            submission=submission,
            comment=comment_text,
            user=request.user,
            parent_comment=parent
            )
        comment.save()
        if request.is_ajax():
            color_helper = UserColors(request)
            comment_dict = comment.to_dict()
            comment_dict['user']['color'] = color_helper.get(comment.user.username)
            return JsonResponse(comment_dict)
        else:
            messages.success(
                request,
                "<strong>Success!</strong> " \
                "Your comment was added to the discussion."
            )
    else:
        error_msg = "<strong>Oops!</strong> Your comment was blank."
        if request.is_ajax():
            return HttpResponseBadRequest(error_msg)
        else:
            messages.error(request, error_msg)
    return HttpResponseRedirect(reverse(
        'datalocker:submission_view',
        kwargs={'locker_id': locker_id, 'submission_id': submission_id }
        ))


@login_required
@require_http_methods(["POST"])
def comment_modify(request, locker_id, submission_id):
    """
    Modifies the existing comment if it is still editable
    """
    comment = get_object_or_404(Comment, id=request.POST.get('id', ''))
    if comment.is_editable:
        comment_text = request.POST.get('comment', '').strip()
        comment.comment = comment_text
        comment.save()
        if request.is_ajax():
            return JsonResponse({
                'comment': comment_text,
                'id': comment.id,
                })
        else:
            messages.success(
                request,
                "<strong>Success!</strong> " \
                "Your comment was added to the discussion."
            )
    else:
        error_msg = "<strong>D'oh!</strong> This comment is no longer editable."
        if request.is_ajax():
            return HttpResponseBadRequest(error_msg)
        else:
            messages.warning(request, error_msg)
    return HttpResponseRedirect(reverse(
        'datalocker:submission_view',
        kwargs={'locker_id': locker_id, 'submission_id': submission_id }
        ))


@login_required
@require_http_methods(["GET", "HEAD"])
def comments_list(request, locker_id, submission_id):
    """
    Returns a list of comments for the specified submission
    """
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.locker.discussion_enabled():
        if submission.locker.is_owner(request.user) or (
            submission.locker.is_user(request.user) and submission.locker.discussion_users_have_access()
        ):
            if request.is_ajax():
                color_helper = UserColors(request)
                comments = []
                comment_objs = submission.comments.order_by(
                    'parent_comment', '-timestamp'
                )
                for comment in comment_objs:
                    comment_dict = comment.to_dict()
                    comment_dict['user']['color'] = color_helper.get(
                        comment.user.username
                    )
                    comments.append(comment_dict)
                return JsonResponse({
                    'discussion': comments,
                    'editing_time_value': settings.COMMENT_EDIT_MAX,
                    'editing_time_units': 'minutes',
                    })
    return HttpResponseRedirect(reverse(
        'datalocker:submission_view',
        {'locker_id': locker_id, 'submission_id': submission_id }
        ))



def custom_404(request):
    response = render_to_response('datalocker/404.html')
    response.status_code = 404
    return response




def forbidden_view(request):
    """
    Displays a custom forbidden (403) page
    """
    return render(request, 'datalocker/403.html', {})


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


@login_required()
@require_http_methods(["GET", "HEAD"])
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
    template_name = 'datalocker/submissions_list.html'


    def get_context_data(self, **kwargs):
        context = super(LockerSubmissionsListView, self).get_context_data(**kwargs)
        locker = Locker.objects.get(pk=self.kwargs['locker_id'])
        context['locker'] = locker
        fields_list = locker.get_all_fields_list()
        context['fields_list'] = fields_list
        selected_fields = locker.get_selected_fields_list()
        context['selected_fields'] = selected_fields
        context['column_headings'] = ['Submitted date', ] + selected_fields
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


@login_required()
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


def not_found_view(request):
    """
    Displays a custom not found (404) page
    """
    return render(request, 'datalocker/404.html', {})


def server_error_view(request):
    """
    Displays a custom internal server error (500) page
    """
    return render(request, 'datalocker/500.html', {})


@login_required()
@require_http_methods(["POST"])
def submission_delete(request, locker_id, submission_id):
    """
    Marks a submission as deleted in the database.
    """
    if request.is_ajax():
        submission = get_object_or_404(Submission, id=submission_id)
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
            'datalocker:submissions_list',
            kwargs={'locker_id': locker_id}
            ))


@login_required()
@require_http_methods(["POST"])
def submission_undelete(request, locker_id, submission_id):
    """
    Removes the deleted timestamp from a submission
    """
    if request.is_ajax():
        submission = get_object_or_404(Submission, id=submission_id)
        submission.deleted = None
        submission.save()
        return JsonResponse({
            'id': submission.id,
            'timestamp': submission.timestamp,
            })
    else:
        return HttpResponseRedirect(reverse(
            'datalocker:submissions_list',
            kwargs={'locker_id': locker_id}
            ))


@login_required()
@require_http_methods(["GET", "HEAD"])
def submission_view(request, locker_id, submission_id):
    """
    Displays an individual submission
    """
    submission = get_object_or_404(Submission, pk=submission_id)
    oldest = Submission.objects.oldest(submission.locker)
    older = submission.older()
    newer = submission.newer()
    newest = Submission.objects.newest(submission.locker)
    workflow_enabled = submission.locker.workflow_enabled()
    discussion_enabled = submission.locker.discussion_enabled()

    # generate a message to the user if the submission is deleted
    if submission.deleted:
        purge_date = submission.deleted
        purge_date += datetime.timedelta(days=settings.SUBMISSION_PURGE_DAYS)
        messages.warning(
            request,
            "<strong>Heads up!</strong> This submission has been deleted " \
            "and <strong>will be permanently removed</strong> from the " \
            "locker <strong>%s</strong>." % (
                naturaltime(purge_date)
                )
            )
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
        'workflow_users_can_edit': submission.locker.workflow_users_can_edit() or submission.locker.owner == request.user.username,
        'workflow_states': submission.locker.workflow_states(),
        'workflow_state': submission.workflow_state,

        'discussion_enabled': discussion_enabled,
        'discussion_users_have_access': submission.locker.discussion_users_have_access() or submission.locker.owner == request.user.username,

        'sidebar_enabled': workflow_enabled or discussion_enabled,
        })


@login_required
@require_http_methods(["POST"])
def unarchive_locker(request, locker_id):
    locker = get_object_or_404(Locker, id=locker_id)
    owner = locker.owner
    locker.archive_timestamp = None
    locker.save()
    return HttpResponseRedirect(reverse('datalocker:index'))


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


@login_required()
@require_http_methods(["POST"])
def workflow_modify(request, locker_id, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    new_state = request.POST.get('workflow-state', '')
    if new_state in submission.locker.workflow_states():
        submission.workflow_state = new_state
        submission.save()
        if request.is_ajax():
            return JsonResponse({
                'state': new_state
                })
    else:
        error_msg = "<strong>Oops!</strong> Unknown workflow state specified."
        if request.is_ajax():
            return HttpResponseBadRequest(error_msg, content_type='text/plain');
        else:
            messages.error(request, error_msg)
    return HttpResponseRedirect(reverse(
        'datalocker:submission_view',
        kwargs={
            'locker_id': submission.locker.id,
            'pk': submission.id,
            }
        ))
