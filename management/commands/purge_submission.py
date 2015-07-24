#!/usr/bin/env python
"""
Shell script to delete the purged submissions after 3 days 
"""

from django.core.management.base import NoArgsCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils import timezone

# from datatime import timedelta
import datetime
from datalocker.models import Locker, Submission

class Command(NoArgsCommand):
    help = 'Deletes the purged submissions after 3 days'

    def handle(self, *args, **options):
        submissions = Submission.objects.all()
        duration = datetime.timedelta(days=3)
        now = datetime.datetime.now(timezone.utc)
    	for submission in submissions:     
            if submission.deleted != None:
                deleted_time = submission.deleted 
                time = now - deleted_time
                if time >= duration:
                    submission.delete()       





