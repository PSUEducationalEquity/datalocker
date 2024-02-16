
def request_is_ajax(self):
    """Method for the HttpRequest object

    This was removed in Django 4.0 because it is jQuery dependent and
    use of jQuery is not common anymore. Piko still uses jQuery heavily,
    so this method can be used to monkey patch the functionality back in.
    """
    return self.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
