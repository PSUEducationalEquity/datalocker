from functools import wraps

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import available_attrs


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
