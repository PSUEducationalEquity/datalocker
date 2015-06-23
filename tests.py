from datalocker.models import Locker, Submission
from django.test import TestCase
from django.utils import timezone


import datetime


# Create your tests here.
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

