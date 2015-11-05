from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import available_attrs

from .models import Locker, Submission


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    Decorator for views that checks that the user is logged in AND an active
    user, redirecting to the log-in page if necessary.
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
    """
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
    """
    Decorator ...
    """
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view_func(request, *args, **kwargs):
        if 'submission_id' in kwargs:
            submission = get_object_or_404(Submission, pk=kwargs['submission_id'])
            locker = submission.locker
        elif 'locker_id' in kwargs:
            locker = get_object_or_404(Locker, pk=kwargs['locker_id'])
        if not locker:
            raise SuspiciousOperation
        if not locker.has_access(request.user):
            raise PermissionDenied
        if submission:
            # redirect these views to the submissions list, otherwise submission view
            redirect_to_list = (
                'submission_delete',
                'submission_undelete'
                )
            if submission.locker.id != int(kwargs['locker_id']):
                if request.resolver_match.url_name in redirect_to_list:
                    view = reverse(
                        'datalocker:submissions_list',
                        kwargs={'locker_id': kwargs['locker_id']}
                        )
                    msg = "<strong>Oops!</strong> The submission you " \
                        + "requested is not in the locker you specified, " \
                        + "but here are the submissions that are in the locker."
                    messages.error(request, msg)
                else:
                    view = reverse(
                        'datalocker:submission_view',
                        kwargs={
                            'locker_id': submission.locker.id,
                            'submission_id': submission.id }
                        )
                return HttpResponseRedirect(view)
        response = view_func(request, *args, **kwargs)
        return response
    return _wrapped_view_func
