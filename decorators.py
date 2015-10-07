from functools import wraps

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.utils.cache import patch_response_headers
from django.utils.decorators import available_attrs

from .models import Locker, LockerQuerySet

def user_has_locker_access(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        try:
            locker = Locker.objects.get(pk=kwargs['locker_id'])
        except (Locker.DoesNotExist, KeyError):
            locker_access = False
        else:
            locker_access = locker.has_access(request.user)
        if request.user.is_superuser or (request.user.is_active and locker_access):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied
    return _wrapped_view_func


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
        response['Cache-Control'] = 'no-cache,no-store'
        response['Pragma'] = 'no-cache'
        response['Expires'] = 'Tue, 01 Jan 1980 1:00:00 GMT'
        return response
    return _wrapped_view_func
