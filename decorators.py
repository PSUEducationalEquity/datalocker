from django.http import HttpResponseRedirect

from .models import Locker

def user_has_locker_access(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        try:
            locker = Locker.objects.get(pk=kwargs['locker_id'])
        except (Locker.DoesNotExist, KeyError):
            locker_access = True
        else:
            locker_access = locker.has_access(request.user)
        if request.user.is_active and locker_access:
            return view_func(request, *args, **kwargs)
        return HttpResponseRedirect('http://google.com')
    return _wrapped_view_func