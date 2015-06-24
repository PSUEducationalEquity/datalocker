from django.test import TestCase
from django.utils import timezone

from datalocker.models import Locker, Submission

import datetime


# Create your tests here.

class LockerManagerTestCase(TestCase):
    fixtures = [
        'dev-users.yaml',
        'dev-locker.yaml',
        'dev-submission.yaml',
        ]


    def test_has_access(self):
        s = datalocker.objects.all()
        self.assertItemsEqual([ locker.pk for locker in Locker.objects.has_access()],(1, 2, 3,))


    def test_is_active(self):
        s = datalocker.objects.all()
        self.assertItemsEqual([ locker.pk for locker in Locker.objects.active()],(1, 2, 3, 4, 5, 6, 7,))


    def test_is_archived(self):
        s = datalocker.objects.all()
        self.assertItemsEqual([ locker.pk for locker in Locker.objects.is_archived()],(0, ))




class SubmissionTestCase(TestCase):
    fixtures = [
        'dev-users.yaml',
        'dev-locker.yaml',
        'dev-submission.yaml',
        ]


    def test_data_dict(self):
        """
        data_dict should properly convert JSON formatted text in the `data`
        property into a python dictionary
        """
        s = Submission(data ='{"name": "George", "Gender": "Male"}')
        self.assertDictEqual(
            s.data_dict(),
            { 
                u'name': u'George',
                u'Gender': u'Male',
                }
            )


    def test_to_dict(self):
        """
        to_dict method should properly convert the object to a dictionary
        """
        ### TODO: figure out why the timestamp property isn't output
        #         as part of the to_dict() conversion.
        self.maxDiff = None
        self.assertDictEqual(
            Submission.objects.get(pk=1).to_dict(),
            {
                u'id': 1L,
                'locker': 1L,
                'data': [{
                    u'user': u'das66', 
                    u'name': u'Dominick Stuck', 
                    u'submitted-timestamp': u'2015-01-14 15:00:00-05:00', 
                    u'archive-timestamp': u'2015-02-16 14:02:20-05:00'
                    }, ]
                }
            )
