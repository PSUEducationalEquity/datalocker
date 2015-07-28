#!/usr/bin/env python
### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###
"""
Shell script to delete the purged submissions after 3 days 
"""

from django.core.management.base import NoArgsCommand, CommandError
from django.core.urlresolvers import reverse
from django.utils import timezone

from datalocker.models import Locker, Submission

import datetime



class Command(NoArgsCommand):
    help = 'Deletes the purged submissions after 3 days'

    def handle(self, *args, **options):
        now = timezone.now()
        oldest_date = now - datetime.timedelta(days=3)
        submissions = Submission.objects.filter(deleted__lt=oldest_date)        
    	for submission in submissions:             
            submission.delete()     