from datalocker.models import Locker, Submission
from django.test import TestCase
from django.utils import timezone
from datalocker.models import LockerManager, Locker
from django.test import TestCase


import datetime


# Create your tests here.

class Tests(TestCase):
    fixtures = ['/datalocker_proj/datalocker/fixtures/dev-locker.yaml/',]
    fixtures = ['/datalocker_proj/datalocker/fixtures/dev-submission.yaml/',]
    fixtures = ['/datalocker_proj/datalocker/fixtures/dev-users.yaml/',]


	def test_archived(self):
	    s= Locker.objects.all()
        self.assertItemsEqual([ locker.pk for locker in Locker.objects.archive()],(3, 4, ))


	def test_has_access(self):
        s = datalocker.objects.all()
        self.assertItemsEqual([ locker.pk for locker in Locker.objects.has_access()],(1, 2, 3,))


	def test_is_active(self):
        s = datalocker.objects.all()
        self.assertItemsEqual([ locker.pk for locker in Locker.objects.active()],(1, 2, 3, 4, 5, 6, 7,))


	def test_is_archived(self):
        s = datalocker.objects.all()
        self.assertItemsEqual([ locker.pk for locker in Locker.objects.is_archived()],(0, ))


class DictionTests(TestCase):
    def test_data_dict(self):
        """
        data_dict should properly convert json into a python object
        """
        s = Submission(data ='{"name": "George", "Gender": "Male"}')
        s.data_dict()['name']
        self.assertDictEqual(s.data_dict()['name'], "u'George'")


    def test_to_dict(self):
        """
        to_dict should properly convert python into a diction format
        """
        s = Submission(data = '{"name": "Jeff", "Gender": "Male"}')
        s.data_dict()['name']
        s.to_dict()
        result['data'] = self.data_dict()
        self.assertDictEqual(result, "u'Jeff'")
