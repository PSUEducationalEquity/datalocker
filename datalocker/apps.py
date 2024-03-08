from django.apps import AppConfig


class DataLockerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Data Locker'
    label = 'datalocker'

    def ready(self):
        from datalocker.utils.request_is_ajax import request_is_ajax
        from django.http.request import HttpRequest
        if not hasattr(HttpRequest, 'is_ajax'):
            HttpRequest.is_ajax = request_is_ajax

        try:
            import djpennstate.signals.newuserlookup
        except ImportError:
            pass
