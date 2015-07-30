### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.###

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone

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
            (1, 2, 3, 4, 5, 6, 7, )
            )


    def test_archived(self):
        """
        Tests for archived lockers, there are two archived fixtures and one here
        therefore there should be three returned.
        """
        locker = Locker(
            form_url='http://equity.psu.edu/contact-form',
            form_identifier='contact-form',
            name='Contact Us',
            owner='das66',
            create_timestamp='2015-01-14 15:00:00+05:00',
            archive_timestamp='2015-05-20 15:10:12+05:00',
            )
        locker.save()
        archived = Locker.objects.exclude(archive_timestamp=None)
        self.assertEqual(len(archived), 3)


    def test_has_access(self):
        """
        Returns only those lockers that the specified user has access to
        """
        user = User.objects.get(pk=2)
        self.assertItemsEqual(
            [ locker.pk for locker in Locker.objects.has_access(user) ],
            (1, )
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
        to_dict method should properly convert the object to a dictionary
        """
        ### TODO: figure out why the timestamp property isn't output
        #         as part of the to_dict() conversion.
        expectedResult = {
            'deleted': None,
            u'id': 1L,
            'locker': 1L,
            'data': [{
                u'Name of Organization, Group, or Commonwealth Campus:': u'PSU Altoona',
                u'Event/project name:': u'History Funding',
                u'First Name of Contact Person:': u'Steve',
                u'Last Name of Contact Person:': u'Perso',
                u'University mailing address:': u'eeqdev+dl-psuAltoona@psu.edu',
                u'Penn State email address:': u'eeqdev+dl-sperso@psu.edu',
                u'Phone number: (Include Area Code)': u'457-784-7878',
                u'Date of event:': u'10-15-15',
                u'Amount of funding requested from CFW ($250 maximum per year for each group, or $300 maximum per campus liaison):': u'150',
                u'Please describe how the funds will be used:': u'To buy technologies to help teach history',
                u'What is the anticipated outcome for your project/event?:': u'To help history become an easier to learn subject',
                u'Please explain how your request supports the mission of the Commission for Women:': u'It provides better students through better teachings',
                u'Have you requested funding from other sources?:': u'Yes',
                u'Name of Source:': u'I dont remember',
                u'Amount requested:': u'1500',
                u'Amount received:': u'1499',
                u'Name of Commonwealth Campus Financial Officer:': u'James Bucannon',
                u'Email of Commonwealth Campus Financial Officer:': u'eeqdev+dl-jbucannon@psu.edu',
                u'If your funding request supports a registered student organization, please provide the appropriate ASA account number:': u'124'
                }],


        }
        self.maxDiff = None
        self.assertDictEqual(
            Submission.objects.get(pk=1).to_dict(),
            expectedResult
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
        submission - Submission(
            locker=locker,
            timestamp='2015-01-14 15:00:00+05:00',
            data= {
                'name': 'George',
                'DOB': '02/12/65',
                'Profession': 'IT Manager',
                },
            )
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


    def test_submission_view_new_submission_existing_locker_with_multiple_submissions(self):
        """
        Form submission should add the submission to an existing locker with an
        existing submsision.
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
            self.assertEqual(len(locker.submissions.all()), 2)


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