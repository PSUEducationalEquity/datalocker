### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import login as auth_login, \
    logout as auth_logout, \
    password_change as auth_password_change, \
    password_change_done as auth_password_change_done
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.exceptions import PermissionDenied
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

from .decorators import login_required, never_cache, prevent_url_guessing
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
## Views
##

@login_required
@never_cache
@prevent_url_guessing
@require_http_methods(["POST"])
def comment_add(request, locker_id, submission_id):
    """
    Adds a comment or reply to the specified submission
    """
    submission = get_object_or_404(Submission, id=submission_id)
    comment_text = request.POST.get('comment', '').strip()
    parent_id = request.POST.get('parent', None)
    try:
        parent = Comment.objects.get(pk=parent_id)
    except Comment.DoesNotExist:
        parent = None
    if comment_text:
        comment = Comment(
            submission=submission,
            comment=comment_text,
            user=request.user,
            parent=parent
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
        kwargs={'locker_id': locker_id, 'submission_id': submission_id}
        ))


@login_required
@never_cache
@prevent_url_guessing
@require_http_methods(["POST"])
def comment_modify(request, locker_id, submission_id):
    """
    Modifies the existing comment if it is still editable
    """
    comment = get_object_or_404(Comment, id=request.POST.get('id', ''))
    if comment.is_editable and comment.user == request.user:
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
        kwargs={
            'locker_id': comment.submission.locker.id,
            'submission_id': comment.submission.id,
            }
        ))


@login_required
@never_cache
@prevent_url_guessing
@require_http_methods(["GET", "HEAD"])
def comments_list(request, locker_id, submission_id):
    """
    Returns a list of comments for the specified submission
    """
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.locker.discussion_enabled():
        if submission.locker.is_owner(request.user) or (
            submission.locker.is_user(request.user) and submission.locker.discussion_users_have_access()
        ) or request.user.is_superuser:
            if request.is_ajax():
                color_helper = UserColors(request)
                comments = []
                comment_objs = submission.comments.order_by(
                    'parent', '-timestamp'
                )
                for comment in comment_objs:
                    comment_dict = comment.to_dict()
                    comment_dict['user']['color'] = color_helper.get(
                        comment.user.username
                    )
                    if comment.user != request.user:
                        comment_dict['editable'] = False
                    comments.append(comment_dict)
                return JsonResponse({
                    'discussion': comments,
                    'editing_time_value': settings.COMMENT_EDIT_MAX,
                    'editing_time_units': 'minutes',
                    })
    return HttpResponseRedirect(reverse(
        'datalocker:submission_view',
        kwargs={'locker_id': locker_id, 'submission_id': submission_id}
        ))


@csrf_exempt
@never_cache
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
        'owner_name': request.POST.get('owner', '').strip(),
        'data': request.POST.get('data', '').strip(),
        }
    try:
        safe_values['owner'] = User.objects.get(username=safe_values['owner_name'])
    except User.DoesNotExist:
        safe_values['owner'] = None
    try:
        locker = Locker.objects.filter(
            form_url=safe_values['url'],
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
    else:
        if locker.owner:
            safe_values['owner'] = locker.owner
    if locker.workflow_enabled:
        workflow_state = locker.workflow_default_state()
    else:
        workflow_state = ''
    submission = Submission(
        locker = locker,
        workflow_state = workflow_state,
        data = safe_values['data'],
        )
    submission.save()
    logger.info("New submission (%s) from %s saved to %s locker (%s)" % (
        submission.pk,
        safe_values['url'],
        'new' if created else 'existing',
        locker.pk
        ))

    notify_addresses = []
    if not safe_values['owner']:
        logger.warning("New submission saved to orphaned locker: %s" % (
            reverse(
                'datalocker:submission_view',
                kwargs={'locker_id': locker.id, 'submission_id': submission.id}
                ),
        ))
    else:
        notify_addresses.append(safe_values['owner'].email)
    if locker.shared_users_notification():
        for user in locker.users.all():
            notify_addresses.append(user.email)
    if notify_addresses:
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
                            kwargs={'locker_id': locker.id, 'submission_id': submission.id}
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
                for to_email in notify_addresses:
                    send_mail(subject, message, from_addr, [to_email])
            except:
                logger.exception("New submission email to the locker owner failed")
    return HttpResponse(status=201)


@login_required
@never_cache
@prevent_url_guessing
@require_http_methods(["POST"])
def locker_archive(request, locker_id):
    locker = get_object_or_404(Locker, id=locker_id)
    locker.archive_timestamp = timezone.now()
    locker.save()
    if request.is_ajax():
        return JsonResponse({'locker_id': locker_id})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))


@login_required()
@never_cache
@require_http_methods(["GET", "HEAD"])
def locker_list_view(request):
    """
    Returns a list of lockers owned by the current user and a list of those
    lockers shared with the current user.
    """
    context = {}
    context['owned'] = Locker.objects.active().has_access(
        request.user
    ).annotate(
        latest_submission=Max('submissions__timestamp')
    ).order_by('name').filter(owner=request.user)
    context['shared'] = Locker.objects.active().has_access(
        request.user
    ).annotate(
        latest_submission=Max('submissions__timestamp')
    ).order_by('name').exclude(owner=request.user)

    if request.user.is_superuser:
        context['all'] = Locker.objects.all().annotate(
            latest_submission=Max('submissions__timestamp')
        ).order_by('name')
        context['orphaned'] = Locker.objects.filter(owner=None).annotate(
            latest_submission=Max('submissions__timestamp')
        ).order_by('name')

    return render(request, 'datalocker/index.html', context)


@login_required
@never_cache
@prevent_url_guessing
@require_http_methods(["POST"])
def locker_unarchive(request, locker_id):
    locker = get_object_or_404(Locker, id=locker_id)
    locker.archive_timestamp = None
    locker.save()
    if request.is_ajax():
        return JsonResponse({'locker_id': locker_id})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))


@login_required()
@never_cache
@prevent_url_guessing
@require_http_methods(["POST"])
def locker_user_add(request, locker_id):
    """
    Adds the indicated user to the locker's list of users
    """
    if request.is_ajax():
        locker =  get_object_or_404(Locker, id=locker_id)
        user = get_object_or_404(User, email=request.POST.get('email', ''))
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
@never_cache
@prevent_url_guessing
@require_http_methods(["POST"])
def locker_user_delete(request, locker_id):
    """
    Removes the indicated user from the locker's list of users
    """
    if request.is_ajax():
        locker =  get_object_or_404(Locker, id=locker_id)
        try:
            user = get_object_or_404(User, id=request.POST.get('id', ''))
        except ValueError:
            error_msg = "An invalid user was requested to be deleted."
            return HttpResponseBadRequest(error_msg)
        else:
            if user in locker.users.all():
                locker.users.remove(user)
                locker.save()
            return JsonResponse({'user_id': user.id})
    if error_msg:
        error_msg = "<strong>Oops</strong> %s" % error_msg
        messages.error(request, error_msg)
    return HttpResponseRedirect(reverse('datalocker:index'))


@login_required()
@never_cache
@prevent_url_guessing
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


@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          current_app=None, extra_context=None):
    return auth_login(
        request,
        template_name,
        redirect_field_name,
        authentication_form,
        current_app,
        extra_context
        )


@never_cache
def logout(request, next_page=None,
           template_name='registration/logged_out.html',
           redirect_field_name=REDIRECT_FIELD_NAME,
           current_app=None, extra_context=None):
    return auth_logout(
        request,
        next_page,
        template_name,
        redirect_field_name,
        current_app,
        extra_context
        )


@login_required()
@never_cache
@prevent_url_guessing
@require_http_methods(["POST"])
def modify_locker(request, **kwargs):
    """
    Modifies locker name, ownership, and settings.
    """
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    previous_owner = locker.owner
    if not locker.owner:
        previous_owner = request.user
    new_locker_name = request.POST.get('locker-name', '')
    new_owner_email = request.POST.get('locker-owner', '')
    if new_locker_name != "":
        locker.name = new_locker_name
    if new_owner_email != "":
        try:
            new_owner = User.objects.get(email=new_owner_email)
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


@never_cache
def password_change(request,
                    template_name='registration/password_change_form.html',
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    current_app=None, extra_context=None):
    return auth_password_change(
        request,
        template_name,
        post_change_redirect,
        password_change_form,
        current_app,
        extra_context
        )


@never_cache
def password_change_done(request,
                         template_name='registration/password_change_done.html',
                         current_app=None, extra_context=None):
    return auth_password_change_done(
        request,
        template_name,
        current_app,
        extra_context
        )


@login_required()
@never_cache
@prevent_url_guessing
@require_http_methods(["POST"])
def submission_delete(request, locker_id, submission_id):
    """
    Marks a submission as deleted in the database.
    """
    if request.is_ajax():
        submission = get_object_or_404(Submission, id=submission_id)
        submission.deleted = timezone.now()
        submission.save()
        return JsonResponse({
            'id': submission.id,
            'timestamp': submission.timestamp,
            'deleted': submission.deleted,
            'purge_timestamp': submission.purge_date,
            })
    else:
        return HttpResponseRedirect(reverse(
            'datalocker:submissions_list',
            kwargs={'locker_id': locker_id}
            ))


@login_required()
@never_cache
@prevent_url_guessing
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
@never_cache
@prevent_url_guessing
@require_http_methods(["GET", "HEAD"])
def submission_view(request, locker_id, submission_id):
    """
    Displays an individual submission
    """
    submission = get_object_or_404(Submission, pk=submission_id)
    oldest = Submission.objects.oldest(submission.locker)
    if not oldest:
        oldest = submission
    older = submission.older()
    newer = submission.newer()
    newest = Submission.objects.newest(submission.locker)
    if not newest:
        newest = submission
    workflow_enabled = submission.locker.workflow_enabled()
    discussion_enabled = submission.locker.discussion_enabled()

    # generate a message to the user if the submission is deleted
    if submission.deleted:
        messages.warning(
            request,
            "<strong>Heads up!</strong> This submission has been deleted " \
            "and <strong>will be permanently removed</strong> from the " \
            "locker <strong>%s</strong>." % (
                naturaltime(submission.purge_date)
                )
            )
    return render(request, 'datalocker/submission_view.html', {
        'submission': submission,
        'data': submission.data_dict(with_types=True),

        'oldest': oldest,
        'older': older,
        'newer': newer,
        'newest': newest,
        'oldest_disabled': True if submission.id == oldest.id else False,
        'older_disabled': True if submission.id == older.id else False,
        'newer_disabled': True if submission.id == newer.id else False,
        'newest_disabled': True if submission.id == newest.id else False,

        'workflow_enabled': workflow_enabled,
        'workflow_users_can_edit': submission.locker.workflow_users_can_edit() or submission.locker.owner == request.user,
        'workflow_states': submission.locker.workflow_states(),
        'workflow_state': submission.workflow_state,

        'discussion_enabled': discussion_enabled,
        'discussion_users_have_access': submission.locker.discussion_users_have_access() or submission.locker.owner == request.user,

        'sidebar_enabled': workflow_enabled or discussion_enabled,
        })


@login_required()
@never_cache
@prevent_url_guessing
@require_http_methods(["GET", "HEAD", "POST"])
def submissions_list_view(request, locker_id):
    """
    Returns a list of submissions for the specified locker.
    """
    locker = get_object_or_404(Locker, pk=locker_id)
    if request.method == 'POST':
        # Save the selected fields to include in the submissions list
        locker.fields_selected(request.POST)
        return HttpResponseRedirect(reverse(
            'datalocker:submissions_list',
            kwargs={'locker_id': locker_id}
            ))

    selected_fields = locker.fields_selected();
    context = {
        'allow_maintenance_mode': request.user == locker.owner or request.user.is_superuser,
        'column_headings': ['Submitted date', ] + selected_fields,
        'data': [],
        'fields_list': locker.fields_all(),
        'linkable_indices': [],
        'locker': locker,
        'purge_days': settings.SUBMISSION_PURGE_DAYS,
        'selected_fields': selected_fields,
        }

    ##
    # Build the data that is made available to the template
    #
    # context['data'] contains all the data and metadata for displaying
    # the list of submissions table.
    #
    # Format:
    #     [
    #         [<list of table cell data>],
    #         submission id,
    #         deleted (True/False),
    #         purged date
    #     ]
    ##
    for submission in locker.submissions.all().order_by('-timestamp'):
        entry_data = [submission.timestamp, ]
        submission_data = submission.data_dict()
        for field in selected_fields:
            try:
                entry_data.append(submission_data[field])
            except KeyError:
                if field == 'Workflow state':
                    entry_data.append(submission.workflow_state)
        context['data'].append([
            entry_data,
            submission.id,
            True if submission.deleted else False,
            submission.purge_date,
            ])

    # determine which indices in the cell data list will be linked
    try:
        context['linkable_indices'].append(
            context['column_headings'].index('Submitted date')
        )
    except ValueError:
        pass
    if not context['linkable_indices']:
        context['linkable_indices'] = [0,]

    return render(request, 'datalocker/submissions_list.html', context)


@never_cache
@require_http_methods(["GET", "HEAD"])
def testing_bad_request_view(request):
    """
    Displays a custom bad request (400) page
    """
    return render(request, '400.html', {})


@never_cache
@require_http_methods(["GET", "HEAD"])
def testing_forbidden_view(request):
    """
    Displays a custom forbidden (403) page
    """
    return render(request, '403.html', {})


@never_cache
@require_http_methods(["GET", "HEAD"])
def testing_not_found_view(request):
    """
    Displays a custom not found (404) page
    """
    return render(request, '404.html', {})


@never_cache
@require_http_methods(["GET", "HEAD"])
def testing_server_error_view(request):
    """
    Displays a custom internal server error (500) page
    """
    return render(request, '500.html', {})


@login_required()
@never_cache
@require_http_methods(["GET", "HEAD"])
def users_list(request, **kwargs):
    """
    Returns a list of all the user email addresses in the system

    This is used to power the owner and shared user auto-complete which is
    driven by TypeAhead.js.
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
@never_cache
@prevent_url_guessing
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
            'submission_id': submission.id,
            }
        ))
