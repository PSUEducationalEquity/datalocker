### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

from collections import OrderedDict

from datalocker.models import Locker, Submission

import datetime, json


class LockerManagerTestCase(TestCase):
    fixtures = [
        'dev-users.yaml',
        'dev-locker.yaml',
        'dev-submission.yaml',
        ]


    def test_active(self):
        """
        Returns only the active (non-archived) lockers
        """
        self.assertItemsEqual(
            [ locker.pk for locker in Locker.objects.active() ],
            (1, 2, 4, 6, )
            )


    def test_archived(self):
        """
        Returns only archived lockers
        """
        self.assertItemsEqual(
            [ locker.pk for locker in Locker.objects.archived() ],
            (3, 5, )
            )


    def test_has_access(self):
        """
        Returns only those lockers that the specified user has access to
        """
        user = User.objects.get(pk=2)
        self.assertItemsEqual(
            [ locker.pk for locker in Locker.objects.has_access(user) ],
            (1, 2, 3, 4, 6, )
            )


    def test_has_access_user_only(self):
        """
        User who does not own any lockers but has lockers shared with him.
        """
        user = User.objects.get(pk=1)
        self.assertItemsEqual(
            [ locker.pk for locker in Locker.objects.has_access(user) ],
            (1, 3, 4, 5, 6, )
            )




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
        to_dict method should properly convert the object to a python dictionary
        """
        data = OrderedDict({
            u'first-name': u'Dominick',
            u'last-name': u'Stuck',
            u'email': u'das66@psu.edu',
            u'subject': u'Testing',
            u'comment': u'Testing the Submission.to_dict() method.',
            })
        submission = Submission(
            locker = Locker.objects.get(pk=1),
            data = json.dumps(data),
            deleted = None
            )
        submission.save()
        expected_results = {
            'deleted': None,
            'locker': 1L,
            'data': data,
            u'id': submission.id,
            'timestamp': submission.timestamp.isoformat(),
            }
        self.maxDiff = None
        self.assertDictEqual(
            submission.to_dict(),
            expected_results
            )




class SubmissionViewTestCase(TestCase):
    def test_submission_view_new_form_entry(self):
        """
        Form submission should create a new locker and save the submission.
        """
        user = User(
            username='das66',
            email='eeq+das66@psu.edu'
            )
        user.save()
        response = self.client.post(
            reverse('datalocker:form_submission'),
            {
                'form-id': 'contact-form',
                'url': 'http://equity.psu.edu/contact-form',
                'owner': 'das66',
                'name': 'Contact Us',
                'data': json.dumps({
                    'Your E-mail Address': 'das66@psu.edu',
                    'Subject': 'New Form Entry Test',
                    'Comments': 'Testing locker creation from initial form submission',
                    }),
            })
        self.assertEqual(response.status_code, 201)
        try:
            locker = Locker.objects.get(form_identifier='contact-form')
        except Locker.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertEqual(len(locker.submissions.all()), 1)


    def test_submission_view_new_submission_existing_locker(self):
        """
        Form submission should add the submission to an existing locker.
        """
        user = User(
            username='das66',
            email='eeq+das66@psu.edu'
            )
        user.save()
        locker = Locker(
            form_url='http://equity.psu.edu/contact-form',
            form_identifier='contact-form',
            name='Contact Us',
            owner='das66',
            create_timestamp='2015-01-14 15:00:00+05:00',
            )
        locker.save()
        response = self.client.post(
            reverse('datalocker:form_submission'),
            {
                'form-id': 'contact-form',
                'url': 'http://equity.psu.edu/contact-form',
                'owner': 'das66',
                'name': 'Contact Us',
                'data': json.dumps({
                    'Your E-mail Address': 'das66@psu.edu',
                    'Subject': 'New Form Entry Test',
                    'Comments': 'Testing locker creation from initial form submission',
                    }),
            })
        self.assertEqual(response.status_code, 201)
        try:
            locker = Locker.objects.get(form_identifier='contact-form')
        except Locker.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertEqual(len(locker.submissions.all()), 1)


    def test_submission_view_archive_locker_create_new_locker(self):
        """
        Form submission should create a new locker because
        the original was archived and save the submission.
        """
        user = User(
            username='das66',
            email='eeqdev+das66@psu.edu'
            )
        user.save()
        locker = Locker(
            form_url='http://equity.psu.edu/contact-form',
            form_identifier='contact-form',
            name='Contact Us',
            owner='das66',
            create_timestamp='2015-01-14 15:00:00+05:00',
            archive_timestamp='2014-04-19 12:00:00+05:00',
            )
        locker.save()
        response = self.client.post(
            reverse('datalocker:form_submission'),
            {
                'form-id': 'contact-form',
                'url': 'http://equity.psu.edu/contact-form',
                'owner': 'das66',
                'name': 'Contact Us',
                'data': json.dumps({
                    'Your E-mail Address': 'das66@psu.edu',
                    'Subject': 'New Form Entry Test',
                    'Comments': 'Testing locker creation from initial form submission',
                    }),
            })
        self.assertEqual(response.status_code, 201)
        try:
            locker = Locker.objects.filter(form_identifier='contact-form')
        except Locker.DoesNotExist:
            self.assertTrue(False)
        else:
            self.assertEqual(len(Locker.objects.all()), 2)
            
            
    def test_submission_view_no_data_submission(self):
        """
        Form submission should add a submission with no data,
        which shouldn't generate any errors to the user.
        """
        locker = Locker(
            form_url='http://equity.psu.edu/contact-form',
            form_identifier='contact-form',
            name='Contact Us',
            owner='das66',
            create_timestamp='2015-01-14 15:00:00+05:00',
            archive_timestamp='2014-04-19 12:00:00+05:00',
            )
        response = self.client.post(
            reverse('datalocker:form_submission'),
            {
                'form-id': 'contact-form',
                'url': 'http://equity.psu.edu/contact-form',
                'owner': 'das66',
                'name': 'Contact Us',
            })
        self.assertEqual(response.status_code, 201)
        submission = Submission.objects.get(id=1)
        submission.data_dict()
        
        