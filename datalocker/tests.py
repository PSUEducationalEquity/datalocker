### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from collections import OrderedDict

from datalocker.models import Locker, Submission

import json


class LockerManagerTestCase(TestCase):
    fixtures = [
        'dev-users.yaml',
        'dev-locker.yaml',
        'dev-submission.yaml',
    ]

    def test_active(self):
        """Only the active (non-archived) lockers"""
        self.assertItemsEqual(
            [locker.pk for locker in Locker.objects.active()],
            [1, 2, 4, 5]
        )

    def test_archived(self):
        """Only archived lockers"""
        self.assertItemsEqual(
            [locker.pk for locker in Locker.objects.archived()],
            [3, ]
        )

    def test_has_access(self):
        """Only lockers the user is as owner or shared user of"""
        user = User.objects.get(pk=2)
        self.assertItemsEqual(
            [locker.pk for locker in Locker.objects.has_access(user)],
            [1, 2, 3, 4]
        )

    def test_has_access_user_only(self):
        """User who owns no lockers but has lockers shared with them"""
        user = User.objects.get(pk=4)
        self.assertItemsEqual(
            [locker.pk for locker in Locker.objects.has_access(user)],
            [3, 4]
        )


class SubmissionTestCase(TestCase):
    fixtures = [
        'dev-users.yaml',
        'dev-locker.yaml',
        'dev-submission.yaml',
    ]

    def test_data_dict(self):
        """Properly convert JSON text in `data` property into a python dict"""
        s = Submission(data='{"name": "George", "Gender": "Male"}')
        self.assertDictEqual(
            s.data_dict(),
            {
                u'name': u'George',
                u'Gender': u'Male',
            }
        )

    def test_to_dict(self):
        """to_dict method should convert the object to a python dict"""
        data = OrderedDict({
            u'first-name': u'Bart',
            u'last-name': u'Simpson',
            u'subject': u'Testing',
            u'comment': u'Testing the Submission.to_dict() method.',
        })
        submission = Submission.objects.create(
            locker=Locker.objects.get(pk=1),
            data=json.dumps(data),
        )
        expected_results = {
            'deleted': None,
            'locker': 1,
            'data': data,
            u'id': submission.id,
            'timestamp': submission.timestamp.isoformat(),
            'workflow_state': '',
        }
        self.maxDiff = None
        self.assertDictEqual(submission.to_dict(), expected_results)


class FormSubmissionTestCase(TestCase):

    def test_new_form_entry(self):
        """Form submission should create a new locker and save the data"""
        User.objects.create(
            username='das66',
            email='eeqdev+das66@psu.edu'
        )
        self.assertEqual(Locker.objects.count(), 0)
        response = self.client.post(
            reverse('datalocker:form_submission'),
            {
                'form-id': 'contact-form',
                'url': 'http://equity.psu.edu/contact-form',
                'owner': 'das66',
                'name': 'Contact Us',
                'data': json.dumps({
                    'Your E-mail Address': 'eeqdev+das66@psu.edu',
                    'Subject': 'New Form Entry Test',
                    'Comments': 'Testing locker creation from initial form submission',  # NOQA
                }),
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Locker.objects.count(), 1)
        lockers = Locker.objects.filter(form_identifier='contact-form')
        self.assertEqual(lockers.count(), 1)

    def test_new_submission_existing_locker(self):
        """Form submission should add the submission to an existing locker"""
        user = User.objects.create(
            username='das66',
            email='eeqdev+das66@psu.edu'
        )
        Locker.objects.create(
            form_url='http://equity.psu.edu/contact-form',
            form_identifier='contact-form',
            name='Contact Us',
            owner=user,
            create_timestamp='2015-01-14 15:00:00+05:00',
        )
        self.assertEqual(Locker.objects.count(), 1)
        response = self.client.post(
            reverse('datalocker:form_submission'),
            {
                'form-id': 'contact-form',
                'url': 'http://equity.psu.edu/contact-form',
                'owner': 'das66',
                'name': 'Contact Us',
                'data': json.dumps({
                    'Your E-mail Address': 'eeqdev+das66@psu.edu',
                    'Subject': 'New Form Entry Test',
                    'Comments': 'Testing locker creation from initial form submission',  # NOQA
                }),
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Locker.objects.count(), 1)
        lockers = Locker.objects.filter(form_identifier='contact-form')
        self.assertEqual(lockers.count(), 1)

    def test_archive_locker_create_new_locker(self):
        """Form submission should create a new locker and save the data

        The new locker is created because the original locker was archived.
        """
        user = User.objects.create(
            username='das66',
            email='eeqdev+das66@psu.edu'
        )
        Locker.objects.create(
            form_url='http://equity.psu.edu/contact-form',
            form_identifier='contact-form',
            name='Contact Us',
            owner=user,
            create_timestamp='2014-01-14 15:00:00+05:00',
            archive_timestamp='2014-04-19 12:00:00+05:00',
        )
        self.assertEqual(Locker.objects.count(), 1)
        response = self.client.post(
            reverse('datalocker:form_submission'),
            {
                'form-id': 'contact-form',
                'url': 'http://equity.psu.edu/contact-form',
                'owner': 'das66',
                'name': 'Contact Us',
                'data': json.dumps({
                    'Your E-mail Address': 'eeqdev+das66@psu.edu',
                    'Subject': 'New Form Entry Test',
                    'Comments': 'Testing locker creation from initial form submission',  # NOQA
                }),
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Locker.objects.count(), 2)
        lockers = Locker.objects.filter(form_identifier='contact-form')
        self.assertEqual(lockers.count(), 2)

    def test_no_data_submission(self):
        """Form submission added to the locker with submission date and no data

        The lack of data from the form should not create an error for the user.
        """
        user = User.objects.create(
            username='das66',
            email='eeqdev+das66@psu.edu'
        )
        Locker.objects.create(
            form_url='http://equity.psu.edu/contact-form',
            form_identifier='contact-form',
            name='Contact Us',
            owner=user,
            create_timestamp='2015-01-14 15:00:00+05:00',
            archive_timestamp='2014-04-19 12:00:00+05:00',
        )
        self.assertEqual(Submission.objects.count(), 0)
        response = self.client.post(
            reverse('datalocker:form_submission'),
            {
                'form-id': 'contact-form',
                'url': 'http://equity.psu.edu/contact-form',
                'owner': 'das66',
                'name': 'Contact Us',
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Submission.objects.count(), 1)
        submission = Submission.objects.first()
        self.assertDictEqual(submission.data_dict(), {})
