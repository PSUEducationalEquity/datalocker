### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils import timezone
from django.utils.text import slugify

from collections import OrderedDict

from .helpers import _get_notification_from_address

import datetime
import json
import logging


logger = logging.getLogger(__name__)


class LockerQuerySet(models.query.QuerySet):
    def active(self):
        """Filter only Lockers without an archived timestamp"""
        return self.filter(archive_timestamp=None)


    def archived(self):
        """Filter only Lockers with an archived timestamp"""
        return self.filter(archive_timestamp__isnull=False)


    def has_access(self, user):
        """Filter only lockers that the user has access to

        `user` must be the owner or a shared user of the locker to be
        included in the results.
        """
        return Locker.objects.filter(Q(owner=user) | Q(users=user)).distinct()




class LockerManager(models.Manager):
    def add_submission(self, values, request=None, locker=None):
        """Add a submission to the appropriate locker

        [description]

        Arguments:
            values {dict} -- Python dictionary that includes the following:
                identifier {str} -- unique form identifier name (default: {''})
                name {str} -- name of the locker (default: {'New Locker'})
                url {str} -- URL where the submission came from (default: {''})
                owner {str} -- name of the person who "owns" the form making
                               the submission which is used to determine the
                               owner of the Locker if it is created
                               (default: {''})
                data {str} -- string of JSON-encoded data that is the
                              submission to save (default: {''})

        Keyword Arguments:
            request {obj} -- Django HTTP Request object instance
                             (default: {None})
            locker {Locker} -- Instance of Locker to save the submission to.
                               Will be looked up or created if not specifed.
                               (default: {None})
        """
        def _exists(attr):
            try:
                value = values[attr]
            except KeyError:
                return False
            if value.strip() == '':
                return False
            return True

        created = False
        if locker is not None:
            values['owner'] = locker.owner
            if not _exists('identifier'):
                values['identifier'] = locker.form_identifier
            if not _exists('name'):
                values['name'] = locker.name
            if not _exists('url'):
                values['url'] = locker.form_url
        else:
            try:
                locker = self.filter(
                    form_url=values['url'],
                    archive_timestamp=None,
                ).order_by('-pk')[0]
            except (Locker.DoesNotExist, IndexError):
                locker = self.create(
                    form_identifier=values['identifier'],
                    name=values['name'],
                    form_url=values['url'],
                    owner=values['owner'],
                )
                created = True
            else:
                if locker.owner:
                    values['owner'] = locker.owner
        if locker.workflow_enabled:
            workflow_state = locker.workflow_default_state()
        else:
            workflow_state = ''
        submission = Submission.objects.create(
            locker=locker,
            workflow_state=workflow_state,
            data=values['data'],
        )
        logger.info('New submission ({}) from {} saved to {} locker ({})'.format(  # NOQA
            submission.pk,
            values['url'],
            'new' if created else 'existing',
            locker.pk
        ))

        submission_url = reverse(
            'datalocker:submission_view',
            kwargs={'locker_id': locker.id, 'submission_id': submission.id}
        )
        if request:
            submission_url = request.build_absolute_uri(submission_url)
        locker_url = reverse(
            'datalocker:submissions_list',
            kwargs={'locker_id': locker.id}
        )
        if request:
            locker_url = request.build_absolute_uri(locker_url)
        notify_addresses = []
        if not values['owner']:
            logger.warning('New submission saved to orphaned locker: '
                           '{}'.format(submission_url))
        else:
            notify_addresses.append(values['owner'].email)
        if locker.shared_users_notification():
            for user in locker.users.all():
                notify_addresses.append(user.email)
        if notify_addresses:
            from_addr = _get_notification_from_address('new submission')
            if from_addr:
                subject = '{} - new submission'.format(values['name'])
                message = 'A new form submission was saved to the Data ' \
                          'Locker. The name of the locker and links to view ' \
                          'the submission are provided below.\n\n' \
                          'Locker: {}\n\n' \
                          'View submission: {}\n' \
                          'View all submissions: {}\n'.format(
                              values['name'],
                              submission_url,
                              locker_url,
                          )
                try:
                    for to_email in notify_addresses:
                        send_mail(subject, message, from_addr, [to_email])
                except (BadHeaderError):
                    logger.exception('New submission email to the locker owner failed')  # NOQA


    def get_query_set(self):
        return LockerQuerySet(self.model, using=self._db)


    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)




class Locker(models.Model):
    form_url = models.CharField(
        max_length=255,
        default='',
        blank=True,
    )
    form_identifier = models.CharField(
        max_length=255,
        default='',
        blank=True,
    )
    name = models.CharField(
        max_length=255,
        default='',
        blank=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='lockers_owned',
        default=None,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_lockers',
        blank=True,
    )
    create_timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
    )
    archive_timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        editable=False,
        default=None,
        blank=True,
        null=True,
    )
    objects = LockerManager()


    class Meta:
        permissions = (('add_manual_submission', 'Can add manual submission'), )  # NOQA


    def __str__(self):
        return self.name


    def discussion_enabled(self, enable=None):
        """Get or set whether discussions are enabled for the locker

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        Arguments:
            enable {bool} -- If True, allows discussions on the locker
                             submissions. If False, prevents discussions on the
                             locker submissions. (Default: {None} which returns
                             the current setting)
        """
        setting, created = self._get_or_create_setting(
            category='discussion',
            identifier='enabled',
            setting='Indicates if discussion is enabled or not',
            value=False
        )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()


    def discussion_users_have_access(self, enable=None):
        """Get or set whether shared users have access to discussions

        Arguments:
            enable {bool} -- If True, allows shared users to have access to
                             discussions. If False, prevents shared users from
                             having access to discussions. (Default: {None}
                             which returns the current setting)
        """
        setting, created = self._get_or_create_setting(
            category='discussion',
            identifier='users-have-access',
            setting='Indicates if users have access to discussion',
            value=False
        )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()


    def fields_all(self):
        """List of all the fields that appear in any of the submissions"""
        all_fields_setting, created = self._get_or_create_setting(
            category='fields-list',
            identifier='all-fields',
            setting='List of all fields',
            value=json.dumps([])
        )
        all_fields = json.loads(all_fields_setting.value)
        is_dirty = False

        # include 'Workflow state' if workflow is enabled
        if self.workflow_enabled():
            if 'Workflow state' not in all_fields:
                all_fields.append('Workflow state')
                is_dirty = True
        else:
            try:
                all_fields.remove('Workflow state')
            except ValueError:
                pass
            else:
                is_dirty = True

        # see if there are new submissions to review
        last_updated_setting, created = self._get_or_create_setting(
            category='fields-list',
            identifier='last-updated',
            setting='Date/time all fields list last updated',
            value=timezone.now()
        )
        if created:
            submissions = self.submissions.all()
        else:
            submissions = self.submissions.filter(
                timestamp__gte=last_updated_setting.value)
        for submission in submissions:
            fields = submission.data_dict().keys()
            for field in fields:
                if field not in all_fields:
                    all_fields.append(field)
                    is_dirty = True

        # save the changes
        if is_dirty:
            all_fields_setting.value = json.dumps(all_fields)
            all_fields_setting.save()
            last_updated_setting.value = timezone.now()
            last_updated_setting.save()
        return all_fields


    def fields_selected(self, fields=None):
        """Gets/sets the list of fields to display for a submissions list

        If `fields` is None:

            Returns a list of fields the user selected to be displayed as part
            of the list of submissions

        If `fields` is specified:

            Validates and saves the list of selected fields to display.
            Validation involves ensuring there is a match between each
            specified field and the list of all fields possible for this
            locker.

        Arguments:
            fields {list} -- List of field names or slugified field names to
                             be shown in the tabular view
        """
        setting, created = self._get_or_create_setting(
            category='fields-list',
            identifier='selected-fields',
            setting='User-defined list of fields to display in tabular view',
            value=json.dumps([])
        )
        if fields is None:
            return json.loads(setting.value)
        else:
            selected_fields = []
            for field in self.fields_all():
                if field in fields or slugify(field) in fields:
                    selected_fields.append(field)
            setting.value = json.dumps(selected_fields)
            setting.save()


    def _get_or_create_setting(self, category, identifier, setting, value):
        """Gets or creates a setting for the locker

        Arguments:
            category {str} -- Category for grouping the setting
            identifier {str} -- Identifier for the setting
            setting {str} -- Friendly name of the setting being retrieved
                             or created
            value {str} -- Value to use if the setting is created
        """
        try:
            setting = self.settings.get(
                category=category,
                identifier=identifier
            )
        except LockerSetting.DoesNotExist:
            setting = LockerSetting(
                category=category,
                identifier=identifier,
                locker=self,
                setting=setting,
                value=value
            )
            setting.save()
            self.settings.add(setting)
            self.save()
            return (setting, True)
        else:
            return (setting, False)


    def get_settings(self):
        """Returns a dictionary of all the locker's settings"""
        settings_dict = {}
        for setting in self.settings.all():
            key = "%s|%s" % (setting.category, setting.identifier)
            try:
                value = json.loads(setting.value)
            except:
                if setting.value == "False":
                    value = False
                elif setting.value == "True":
                    value = True
                else:
                    value = setting.value
            settings_dict[key] = value
        return settings_dict


    def has_access(self, user):
        """Returns True if user has access to the locker

        Arguments:
            user {User} -- User instance to check

        Returns:
            {bool} -- True if the user has access to the locker as either the
                      owner, a shared user, or a super user.
        """
        return self.is_owner(user) or self.is_user(user) or user.is_superuser


    def is_archived(self):
        """Returns True if the locker has been archived"""
        return self.archive_timestamp is not None


    def is_owner(self, user):
        """Returns True if user is the locker owner

        Arguments:
            user {User} -- User instance to check

        Returns:
            {bool} -- True if the user is the locker owner
        """
        return user == self.owner


    def is_user(self, user):
        """Returns True if user has shared access to the locker

        Arguments:
            user {User} -- User instance to check

        Returns:
            {bool} -- True if the user has shared access to the locker
        """
        return user in self.users.all()


    def shared_users_notification(self, enable=None):
        """
        Gets or sets the setting on the locker indicating if shared users
        receive an email when a new submission is received.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='submission-notifications',
            identifier='notify-shared-users',
            setting='Indicates if shared users should receive an '
                    'email when a new submission is received',
            value=False
        )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()


    def workflow_default_state(self):
        states = self.workflow_states()
        try:
            return states[0]
        except IndexError:
            return ''


    def workflow_enabled(self, enable=None):
        """Gets or sets the workflow enabled setting on the locker.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='workflow',
            identifier='enabled',
            setting='Indicates if workflow is enabled or not',
            value=False
        )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()
            if not enable:
                # remove the workflow state from the selected fields list
                fields = self.fields_selected()
                try:
                    fields.remove('Workflow state')
                except ValueError:
                    pass
                else:
                    self.fields_selected(fields)


    def workflow_states(self, states=None):
        """
        Gets or sets the workflow setting on the locker indicating the possible
        workflow states.

        Calling it with enable=None will return the current setting value
        as a list.
        Passing it a list of values, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='workflow',
            identifier='states',
            setting='User-defined list of workflow states',
            value=json.dumps([])
        )
        if states is None:
            return json.loads(setting.value)
        else:
            setting.value = json.dumps(
                [item.strip() for item in states.split('\n') if item.strip()]
            )
            setting.save()


    def workflow_users_can_edit(self, enable=None):
        """
        Gets or sets the workflow setting on the locker indicating if shared
        users can change the workflow state.

        Calling it with enable=None will return the current setting value
        as a boolean.
        Passing it a boolean value, will set the value.
        """
        setting, created = self._get_or_create_setting(
            category='workflow',
            identifier='users-can-edit',
            setting='Indicates if users can change the workflow state',
            value=False
        )
        if enable is None:
            return True if setting.value == 'True' else False
        elif enable in (True, False):
            setting.value = str(enable)
            setting.save()




class LockerSetting(models.Model):
    category = models.CharField(
        max_length=255,
    )
    setting = models.CharField(
        max_length=255,
    )
    identifier = models.SlugField()
    value = models.TextField(
        default='',
    )
    locker = models.ForeignKey(
        Locker,
        related_name="settings",
        on_delete=models.CASCADE,
    )




class SubmissionManager(models.Manager):
    def oldest(self, locker):
        """Returns the oldest submission based on the timestamp"""
        try:
            return self.filter(locker=locker, deleted=None).earliest('timestamp')  # NOQA
        except Submission.DoesNotExist:
            return None


    def newest(self, locker):
        """Returns the newest submission based on the timestamp"""
        try:
            return self.filter(locker=locker, deleted=None).latest('timestamp')
        except Submission.DoesNotExist:
            return None




class Submission(models.Model):
    locker = models.ForeignKey(
        Locker,
        related_name="submissions",
        on_delete=models.CASCADE,
    )
    timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
    )
    data = models.TextField(
        default='',
        blank=True,
    )
    deleted = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        editable=False,
        default=None,
        blank=True,
        null=True,
    )
    workflow_state = models.CharField(
        max_length=255,
        default='',
        blank=True,
    )
    objects = SubmissionManager()


    def __str__(self):
        return "%s to %s" % (self.timestamp, self.locker)


    def data_dict(self, with_types=False):
        """Returns the data field as an ordered dictionary"""
        try:
            data = json.loads(self.data, object_pairs_hook=OrderedDict)
        except ValueError:
            data = {}
        if with_types:
            for key, value in data.iteritems():
                headings = []
                if isinstance(value, list):
                    try:
                        if isinstance(value[0], dict) or isinstance(value[0], OrderedDict):  # NOQA
                            # list of dicts which is likely a Data Grid
                            value_type = 'table'
                            rows = []
                            for rowdict in value:
                                if rowdict.get('orderindex_', '') == 'headings':  # NOQA
                                    del rowdict['orderindex_']
                                    headings = rowdict
                                else:
                                    if 'orderindex_' in rowdict.keys():
                                        del rowdict['orderindex_']
                                    rows.append(rowdict)
                            value = rows
                        else:
                            value_type = 'list'
                    except IndexError:
                        value_type = 'list'
                elif isinstance(value, dict) or isinstance(value, OrderedDict):
                    value_type = 'dict'
                else:
                    value_type = 'string'
                data[key] = {
                    'value': value,
                    'type': value_type,
                    'headings': headings,
                }
        return data


    def to_dict(self):
        """Returns the entire object as a Python dictionary"""
        result = model_to_dict(self)
        result['data'] = self.data_dict()
        # model_to_dict skips fields that are not editable and fields that have
        # auto_now_add=True are considered not editable, thus we add the
        # submission timestamp back in manually
        result['timestamp'] = self.timestamp.isoformat()
        result['deleted'] = self.deleted.isoformat() if self.deleted else None
        result['purge_date'] = self.purge_date
        return result


    def newer(self):
        """
        Returns the submission object that was submitted immediately after
        this one. If there isn't a newer submission, the current submission is
        returned.
        """
        try:
            nextSubmission = Submission.objects.filter(
                locker=self.locker,
                timestamp__gt=self.timestamp,
                deleted=None
            ).order_by('timestamp')[0]
        except IndexError:
            return self
        else:
            return nextSubmission


    def older(self):
        """
        Returns the submission object that was submitted immediately before
        this one. If there isn't an older submission, the current submission is
        returned.
        """
        try:
            prevSubmission = Submission.objects.filter(
                locker=self.locker,
                timestamp__lt=self.timestamp,
                deleted=None
            ).order_by('-timestamp')[0]
        except IndexError:
            return self
        else:
            return prevSubmission


    @property
    def purge_date(self):
        """Returns the date that the submission should be deleted"""
        if self.deleted is None:
            return None
        return self.deleted + datetime.timedelta(days=settings.SUBMISSION_PURGE_DAYS)  # NOQA




class Comment(models.Model):
    submission = models.ForeignKey(
        Submission,
        related_name="comments",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="comments",
        on_delete=models.PROTECT,
    )
    timestamp = models.DateTimeField(
        auto_now=False,
        auto_now_add=True,
        editable=False,
    )
    comment = models.TextField(
        default='',
        blank=True,
    )
    parent = models.ForeignKey(
        'self',
        related_name="children",
        default=None,
        blank=True,
        null=True,
    )


    def __str__(self):
        return "%s in %s by %s" % (
            self.submission.timestamp,
            self.submission.locker,
            self.user
        )


    @property
    def is_editable(self):
        """
        Indicates if the comment is editable because it was created within
        COMMENT_EDIT_MAX time till now.
        """
        oldest_timestamp = timezone.now()
        oldest_timestamp -= datetime.timedelta(minutes=settings.COMMENT_EDIT_MAX)  # NOQA
        return True if (self.timestamp > oldest_timestamp) else False


    def to_dict(self):
        """Returns the entire object as a Python dictionary"""
        result = model_to_dict(self)
        result['editable'] = self.is_editable
        # model_to_dict skips fields that are not editable and fields that have
        # auto_now_add=True are considered not editable, thus we add the
        # submission timestamp back in manually
        result['timestamp'] = self.timestamp.isoformat()
        result['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'email': self.user.email,
        }
        return result
