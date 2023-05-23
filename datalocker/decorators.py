from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import available_attrs

from .models import Locker, Submission


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME,
                   login_url=None):
    """Ensure view user is logged in and active

    Decorator for views that checks to ensure the user is logged in AND
    an active user, redirecting to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and u.is_active,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def never_cache(view_func):
    """Adds HTTP headers to the response to block caching

    Decorator that adds headers to a response so that it will
    never be cached.

    Expanded version of django.views.decorators.cache.never_cache that
    adds additional headers that follow the recommendations from:
    http://securityevaluators.com/knowledge/case_studies/caching/
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view_func(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        if response.status_code not in (301, 302):
            response['Cache-Control'] = 'no-cache,no-store'
            response['Pragma'] = 'no-cache'
            response['Expires'] = 'Tue, 01 Jan 1980 1:00:00 GMT'
        return response
    return _wrapped_view_func


def prevent_url_guessing(view_func):
    """Verify permission to lockers/submissions

    Decorator to ensure that the current user has access to the locker
    or submission being accessed. Additionally when a locker and submission
    are specified it ensures that the submission is contained in the
    specified locker.
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view_func(request, *args, **kwargs):
        submission = None
        try:
            locker_id = int(kwargs.get('locker_id', 0))
        except (TypeError, ValueError):
            locker_id = 0
        if 'submission_id' in kwargs:
            submission = get_object_or_404(Submission,
                                           pk=kwargs.get('submission_id', 0))
            locker = submission.locker
        elif 'locker_id' in kwargs:
            locker = get_object_or_404(Locker, pk=locker_id)
        if not locker:
            raise SuspiciousOperation
        if not locker.has_access(request.user):
            raise PermissionDenied
        if submission:
            # redirect these views to the submissions list
            redirect_to_list = ('submission_delete', 'submission_undelete')
            if submission.locker.id != int(locker_id):
                if request.resolver_match.url_name in redirect_to_list:
                    view = reverse('datalocker:submissions_list',
                                   kwargs={'locker_id': locker_id})
                    msg = (u'<strong>Oops!</strong> The submission you '
                           u'requested is not in the locker you specified.')
                    messages.error(request, msg)
                else:
                    view = reverse(
                        'datalocker:submission_view',
                        kwargs={
                            'locker_id': submission.locker.id,
                            'submission_id': submission.id,
                        }
                    )
                return HttpResponseRedirect(view)
        response = view_func(request, *args, **kwargs)
        return response
    return _wrapped_view_func
