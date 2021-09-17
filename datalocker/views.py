### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import (
    login as auth_login,
    logout as auth_logout,
    password_change as auth_password_change,
    password_change_done as auth_password_change_done
)
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.http import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
    JsonResponse,
)
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from smtplib import SMTPException

from .decorators import login_required, never_cache, prevent_url_guessing
from .models import (
    Comment,
    Locker,
    Submission,
)
from .utils.notifications import get_from_address
from .utils.users import get_public_user_dict, UserColors

import logging


logger = logging.getLogger(__name__)


@login_required
@never_cache
@prevent_url_guessing
@require_http_methods(['POST'])
def comment_add(request, locker_id, submission_id):
    """Adds a comment or reply to the specified submission"""
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
            comment_dict['user']['color'] = color_helper.get(comment.user.username)  # NOQA
            return JsonResponse(comment_dict)
        else:
            messages.success(request,
                             u'<strong>Success!</strong> '
                             u'Your comment was added to the discussion.')
    else:
        error_msg = u'<strong>Oops!</strong> Your comment was blank.'
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
@require_http_methods(['POST'])
def comment_modify(request, locker_id, submission_id):
    """Modifies the existing comment if it is still editable"""
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
            messages.success(request,
                             u'<strong>Success!</strong> '
                             u'Your comment was added to the discussion.')
    else:
        error_msg = u"<strong>D'oh!</strong> This comment is no longer editable."  # NOQA
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
@require_http_methods(['GET', 'HEAD'])
def comments_list(request, locker_id, submission_id):
    """Returns a list of comments for the specified submission"""
    submission = get_object_or_404(Submission, pk=submission_id)
    if submission.locker.discussion_enabled():
        is_owner = submission.locker.is_owner(request.user)
        is_user = submission.locker.is_user(request.user)
        discussion_users = submission.locker.discussion_users_have_access()
        if is_owner or (is_user and discussion_users) or request.user.is_superuser:  # NOQA
            if request.is_ajax():
                color_helper = UserColors(request)
                comments = []
                comment_objs = submission.comments.order_by('parent', '-timestamp')  # NOQA
                for comment in comment_objs:
                    comment_dict = comment.to_dict()
                    comment_dict['user']['color'] = color_helper.get(comment.user.username)  # NOQA
                    if comment.user != request.user:
                        comment_dict['editable'] = False
                    comments.append(comment_dict)
                return JsonResponse({
                    'discussion': comments,
                    'editing_time_value': settings.COMMENT_EDIT_MAX,
                    'editing_time_units': 'minutes',
                })
    if request.is_ajax():
        error_msg = u'The user does not have permission to view the discussion.'  # NOQA
        return HttpResponseBadRequest(error_msg)
    else:
        return HttpResponseRedirect(reverse(
            'datalocker:submission_view',
            kwargs={'locker_id': locker_id, 'submission_id': submission_id}
        ))


@csrf_exempt
@never_cache
def form_submission_view(request, **kwargs):
    """Handles submissions from outside forms to be saved in lockers"""
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
        safe_values['owner'] = User.objects.get(username=safe_values['owner_name'])  # NOQA
    except User.DoesNotExist:
        safe_values['owner'] = None
    Locker.objects.add_submission(safe_values, request=request)
    return HttpResponse(status=201)


@login_required
@never_cache
@prevent_url_guessing
@require_http_methods(['POST'])
def locker_archive(request, locker_id):
    """Archive a locker so it receives no new submissions"""
    locker = get_object_or_404(Locker, id=locker_id)
    locker.archive_timestamp = timezone.now()
    locker.save()
    if request.is_ajax():
        return JsonResponse({'locker_id': locker_id})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))


@login_required()
@never_cache
@require_http_methods(['GET', 'HEAD'])
def locker_list_view(request):
    """Return list of lockers for the current user

    The list includes lockers for which the current user is an owner and
    lockers for which the current user is included in the list of shared users.
    """
    context = {}
    context['owned'] = (Locker.objects
                              .active()
                              .has_access(request.user)
                              .include_latest()
                              .filter(owner=request.user))
    context['shared'] = (Locker.objects
                               .active()
                               .has_access(request.user)
                               .include_latest()
                               .exclude(owner=request.user))
    if request.user.is_superuser:
        context['all'] = (Locker.objects.include_latest())
        context['orphaned'] = (Locker.objects
                                     .filter(owner=None)
                                     .include_latest())
    return render(request, 'datalocker/index.html', context)


@login_required
@never_cache
@prevent_url_guessing
@require_http_methods(['POST'])
def locker_unarchive(request, locker_id):
    """Unarchives a locker so it can receive new submissions"""
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
@require_http_methods(['POST'])
def locker_user_add(request, locker_id):
    """Adds the specified user to the locker's list of shared users"""
    if request.is_ajax():
        locker = get_object_or_404(Locker, id=locker_id)
        user = get_object_or_404(User, email=request.POST.get('email', ''))
        if user not in locker.users.all():
            locker.users.add(user)
            from_addr = get_from_address('locker access granted')
            if from_addr:
                subject = u'Access to Locker: {}'.format(locker.name)
                to_addr = user.email
                url = request.build_absolute_uri(reverse(
                    'datalocker:submissions_list',
                    kwargs={'locker_id': locker.id}
                ))
                message = (u'The following Data Locker of form submissions '
                           u'has been shared with you.\n\n'
                           u'Locker: {}\n\n'
                           u'You can view the submissions at:\n{}\n'
                           u''.format(locker.name, url))
                try:
                    send_mail(subject, message, from_addr, [to_addr])
                except SMTPException:
                    logger.exception(u'Locker shared with you email failed to send')  # NOQA
        return JsonResponse({'user': get_public_user_dict(user)})
    else:
        return HttpResponseRedirect(reverse('datalocker:index'))


@login_required()
@never_cache
@prevent_url_guessing
@require_http_methods(['POST'])
def locker_user_delete(request, locker_id):
    """Removes the specified user from the locker's list of users"""
    if request.is_ajax():
        locker = get_object_or_404(Locker, id=locker_id)
        try:
            user = get_object_or_404(User, id=request.POST.get('id', ''))
        except ValueError:
            error_msg = u'An invalid user was requested to be deleted.'
            return HttpResponseBadRequest(error_msg)
        else:
            if user in locker.users.all():
                locker.users.remove(user)
            return JsonResponse({'user_id': user.id})
    if error_msg:
        error_msg = u'<strong>Oops</strong> {}'.format(error_msg)
        messages.error(request, error_msg)
    return HttpResponseRedirect(reverse('datalocker:index'))


@login_required()
@never_cache
@prevent_url_guessing
@require_http_methods(['GET', 'HEAD'])
def locker_users(request, locker_id):
    if request.is_ajax():
        locker = get_object_or_404(Locker, pk=locker_id)
        users = [
            get_public_user_dict(user)
            for user in locker.users.all()
        ]
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
@require_http_methods(['POST'])
def modify_locker(request, **kwargs):
    """Modifies locker name, ownership, and settings"""
    locker = get_object_or_404(Locker, id=kwargs['locker_id'])
    previous_owner = locker.owner
    if not locker.owner:
        previous_owner = request.user
    new_locker_name = request.POST.get('locker-name', '')
    new_owner_email = request.POST.get('locker-owner', '')
    if new_locker_name != '':
        locker.name = new_locker_name
    if new_owner_email != '':
        try:
            new_owner = User.objects.get(email=new_owner_email)
        except User.DoesNotExist:
            logger.error(u'Attempted to reassign locker ({}) '
                         u'to non-existent user ({})'
                         u''.format(locker.name, new_owner_email))
            messages.error(request,
                           u'<strong>Oops!</strong> The user ({}) you tried '
                           u'to make the owner of the <strong>{}</strong> '
                           u'locker does not exist. '
                           u'<strong>You still own the locker.</strong>'
                           u''.format(new_owner_email, locker.name))
        else:
            locker.owner = new_owner
            from_addr = get_from_address(u'change locker owner')
            if from_addr:
                subject = u'Ownership of Locker: {}'.format(locker.name)
                to_addr = new_owner_email
                previous_name = u'{} {}'.format(previous_owner.first_name,
                                                previous_owner.last_name)
                url = request.build_absolute_uri(reverse(
                    'datalocker:submissions_list',
                    kwargs={'locker_id': locker.id}
                ))
                message = (u'{} has changed the ownership of the following '
                           u'locker of form submissions to you.\n\n'
                           u'Locker: {}\n\n'
                           u'You can view the submissions at:\n{}\n'
                           u''.format(previous_name, locker.name, url))
                try:
                    send_mail(subject, message, from_addr, [to_addr])
                except SMTPException:
                    logger.exception(u'Locker ownership changed to you email failed to send')  # NOQA
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
                         template_name='registration/password_change_done.html',  # NOQA
                         current_app=None, extra_context=None):
    return auth_password_change_done(
        request,
        template_name,
        current_app,
        extra_context
    )


@permission_required('datalocker.add_manual_submission')
@login_required()
@require_http_methods(['POST'])
@never_cache
def submission_add(request, locker_id):
    """Manually add a submission to a locker

    Arguments:
        request {obj} -- Django HTTP Request object instance
        locker_id {int} -- Unique identifier for the Locker to add the
                           submission to
    """
    locker = get_object_or_404(Locker, id=locker_id)
    json_data = request.POST.get('json', '').strip()
    json_data = json_data.replace('\r', '')
    json_data = json_data.replace('\n', '')
    json_data = json_data.replace('<div>', '')
    json_data = json_data.replace('</div>', '')
    json_data = json_data.replace('<br />', '\\r\\n')
    json_data = json_data.replace('<br>', '\\r\\n')
    if json_data[-3:] == '",}':
        json_data = json_data[:-3] + '"}'
    Locker.objects.add_submission(
        {'data': json_data},
        request=request,
        locker=locker
    )
    return HttpResponseRedirect(reverse(
        'datalocker:submissions_list',
        kwargs={'locker_id': locker_id}
    ))


@login_required()
@never_cache
@prevent_url_guessing
@require_http_methods(['POST'])
def submission_delete(request, locker_id, submission_id):
    """Marks a submission as deleted"""
    submission = get_object_or_404(Submission, id=submission_id)
    submission.deleted = timezone.now()
    submission.save()
    if request.is_ajax():
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
@require_http_methods(['POST'])
def submission_undelete(request, locker_id, submission_id):
    """Removes the deleted timestamp from a submission"""
    submission = get_object_or_404(Submission, id=submission_id)
    submission.deleted = None
    submission.save()
    if request.is_ajax():
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
@require_http_methods(['GET', 'HEAD'])
def submission_view(request, locker_id, submission_id):
    """Displays an individual submission"""
    submission = get_object_or_404(Submission, pk=submission_id)
    newer = submission.newer()
    newest = Submission.objects.newest(submission.locker)
    if not newest:
        newest = submission
    oldest = Submission.objects.oldest(submission.locker)
    if not oldest:
        oldest = submission
    older = submission.older()
    discussion_enabled = submission.locker.discussion_enabled()
    is_owner = submission.locker.owner == request.user
    users_discussion = submission.locker.discussion_users_have_access()
    users_workflow = submission.locker.workflow_users_can_edit()
    workflow_enabled = submission.locker.workflow_enabled()

    # generate a message to the user if the submission is deleted
    if submission.deleted:
        messages.warning(request,
                         u'<strong>Heads up!</strong> This submission has '
                         u'been deleted and <strong>will be permanently '
                         u'removed</strong> from the locker '
                         u'<strong>{}</strong>.'
                         u''.format(naturaltime(submission.purge_date)))
    return render(request, 'datalocker/submission_view.html', {
        'data': submission.data_dict(with_types=True),
        'discussion_enabled': discussion_enabled,
        'discussion_users_have_access': users_discussion or is_owner,
        'newer': newer,
        'newer_disabled': True if submission.id == newer.id else False,
        'newest': newest,
        'newest_disabled': True if submission.id == newest.id else False,
        'older': older,
        'older_disabled': True if submission.id == older.id else False,
        'oldest': oldest,
        'oldest_disabled': True if submission.id == oldest.id else False,
        'sidebar_enabled': workflow_enabled or discussion_enabled,
        'submission': submission,
        'workflow_enabled': workflow_enabled,
        'workflow_states': submission.locker.workflow_states(),
        'workflow_state': submission.workflow_state,
        'workflow_users_can_edit': users_workflow or is_owner,
    })


@login_required()
@never_cache
@prevent_url_guessing
@require_http_methods(['GET', 'HEAD', 'POST'])
def submissions_list_view(request, locker_id):
    """Returns a list of submissions for the specified locker"""
    locker = get_object_or_404(Locker, pk=locker_id)
    if request.method == 'POST':
        # Save the selected fields to include in the submissions list
        locker.fields_selected(request.POST)
        return HttpResponseRedirect(reverse(
            'datalocker:submissions_list',
            kwargs={'locker_id': locker_id}
        ))
    is_owner = locker.owner == request.user
    selected_fields = locker.fields_selected()
    context = {
        'allow_maintenance_mode': is_owner or request.user.is_superuser,
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
    # the table of submissions.
    #
    # Format:
    #     [
    #         [<list of table cell data>],
    #         submission id,
    #         deleted (True/False),
    #         purged date
    #     ]
    ##
    for submission in locker.submissions.order_by('-timestamp'):
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
        context['linkable_indices'] = [0, ]
    return render(request, 'datalocker/submissions_list.html', context)


@never_cache
@require_http_methods(['GET', 'HEAD'])
def testing_bad_request_view(request):
    """Displays a custom bad request (400) page"""
    return render(request, '400.html', {})


@never_cache
@require_http_methods(['GET', 'HEAD'])
def testing_forbidden_view(request):
    """Displays a custom forbidden (403) page"""
    return render(request, '403.html', {})


@never_cache
@require_http_methods(['GET', 'HEAD'])
def testing_not_found_view(request):
    """Displays a custom not found (404) page"""
    return render(request, '404.html', {})


@never_cache
@require_http_methods(['GET', 'HEAD'])
def testing_server_error_view(request):
    """Displays a custom internal server error (500) page"""
    return render(request, '500.html', {})


@login_required()
@never_cache
@require_http_methods(['GET', 'HEAD'])
def users_list(request, **kwargs):
    """Returns a list of all the user email addresses in the system

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
    return JsonResponse({'users': users_list})


@login_required()
@never_cache
@prevent_url_guessing
@require_http_methods(['POST'])
def workflow_modify(request, locker_id, submission_id):
    submission = get_object_or_404(Submission, pk=submission_id)
    new_state = request.POST.get('workflow-state', '')
    if new_state in submission.locker.workflow_states():
        submission.workflow_state = new_state
        submission.save()
        if request.is_ajax():
            return JsonResponse({'state': new_state})
    else:
        error_msg = u'<strong>Oops!</strong> Unknown workflow state specified.'
        if request.is_ajax():
            return HttpResponseBadRequest(error_msg, content_type='text/plain')
        else:
            messages.error(request, error_msg)
    return HttpResponseRedirect(reverse(
        'datalocker:submission_view',
        kwargs={
            'locker_id': submission.locker.id,
            'submission_id': submission.id,
        }
    ))
