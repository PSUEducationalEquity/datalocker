### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###
"""
Shell script to permanently purge the deleted submissions after a period of time
"""
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils import timezone

from datalocker.models import Submission

import datetime


class Command(NoArgsCommand):
    help = 'Purges the deleted submissions after a period of time'

    def handle(self, *args, **options):
        purge_date = timezone.now() - datetime.timedelta(
            days=settings.SUBMISSION_PURGE_DAYS
            )
        submissions = Submission.objects.filter(deleted__lt=purge_date)
    	for submission in submissions:
            submission.delete()
