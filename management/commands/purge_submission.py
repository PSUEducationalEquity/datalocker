#!/usr/bin/env python
"""
Shell script to delete the purged submissions after 3 days 
"""

from django.core.management.base import NoArgsCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils import timezone
import datetime

from datalocker.models import Locker, Submission

class Command(NoArgsCommand):
    help = 'Deletes the purged submissions after 3 days'
    submissions = Submission.objects.filter(
    	deleted = True
    	)
    duration=datetime.timedelta(days=3)
    def handle_noargs(self, **options):
    	for submission in submissions: 
    		if submission.deleted is not None:
    			if submission.deleted > duration:
    				submission.delete()




