### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils import timezone

from datetime import timedelta

from datalocker.models import Submission


class Command(NoArgsCommand):
    help = 'Purges the deleted submissions after a period of time'

    def handle(self, *args, **options):
        try:
            purge_days = settings.SUBMISSION_PURGE_DAYS
        except AttributeError:
            return
        purge_date = timezone.now() - timedelta(days=purge_days)
        submissions = Submission.objects.filter(deleted__lt=purge_date)
        for submission in submissions:
            submission.delete()
