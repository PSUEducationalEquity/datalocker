### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###
from django.conf import settings

import logging


logger = logging.getLogger(__name__)


def get_from_address(email_purpose):
    """Get the FROM address for notification emails based on the purpose

    FROM addresses should be set using the NOTIFICATIONS_FROM value in
    settings.py. If the setting does not exist or is blank, the error is
    logged and uses `email_purpose` to explain what email was trying
    to be sent.
    """
    from_addr = ''
    try:
        from_addr = settings.NOTIFICATIONS_FROM
    except AttributeError:
        logger.warning('The "{}" email was not sent because '
                       'NOTIFICATIONS_FROM was not defined in '
                       'settings.py'.format(email_purpose))
    else:
        if from_addr == '':
            logger.warning('The "{}" email was not sent because '
                           'NOTIFICATIONS_FROM in settings.py '
                           'is blank'.format(email_purpose))
    return from_addr
