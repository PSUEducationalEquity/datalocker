from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse

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
