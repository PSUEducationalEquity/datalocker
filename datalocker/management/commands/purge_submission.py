### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import termcolors, timezone

from datetime import timedelta

from datalocker.models import Submission


class Command(BaseCommand):
    """Purges the deleted submissions after a period of time"""
    help = __doc__

    def add_arguments(self, parser):
        """Define the command-line arguments for this command"""
        parser.add_argument(
            '-d', '--dryrun',
            action='store_true',
            default=False,
            dest='dryrun',
            help=u'Prevents the command from making any permanent changes',
        )

    def dryrun_write(self, msg, end=None, verbosity=1):
        """Output a message, prefixed with "DryRun:", to the standard output

        Similar to `self.write()` but the message is prefixed with "DryRun: "
        if `self.dryrun` is True. Any indenting spaces are preserved when
        adding the "DryRun: " text.

        Arguments:
            msg {str} -- The message to output to the standard output stream

        Keyword Arguments:
            end {str} -- Override the standard string ending character ('\n')
                         to use something else. Specifying a blank string ('')
                         will keep the next call to `self.write()` on the same
                         line in the terminal. (default: {None})
            verbosity {int} -- What verbosity level the command must be running
                               at for the message to be output (default: {1})
        """
        text_original = msg.strip()
        text_updated = u'{}{}'.format(
            self.style.DRYRUN(u'DryRun: ') if self.dryrun else u'',
            text_original
        )
        msg = msg.replace(text_original, text_updated)
        self.write(msg, end=end, verbosity=verbosity)

    def handle(self, *args, **options):
        """Starting point for all commands"""
        self.style.DRYRUN = termcolors.make_style(fg='white', opts=('bold', ))
        self.dryrun = options['dryrun']
        self.verbosity = options['verbosity']
        try:
            purge_days = settings.SUBMISSION_PURGE_DAYS
        except AttributeError:
            return
        purge_date = timezone.now() - timedelta(days=purge_days)
        self.dryrun_write('Purging submissions deleted before: {}'
                          ''.format(purge_date),
                          verbosity=2)
        submissions = Submission.objects.filter(deleted__lt=purge_date)
        self.write('  {} submissions to purge'.format(submissions.count()),
                   verbosity=3)
        for submission in submissions:
            self.dryrun_write('Purging: {}'.format(submission), verbosity=2)
            if not self.dryrun:
                submission.delete()

    def write(self, msg, end=None, verbosity=1, style=None):
        """Output a message to the standard output stream

        Similar to `self.error()` but the message is directed to the terminal's
        strout stream so that it understands this is a normal output.

        Arguments:
            msg {str} -- The message to output to the standard output stream

        Keyword Arguments:
            end {str} -- Override the standard string ending character ('\n')
                         to use something else. Specifying a blank string ('')
                         will keep the next call to `self.write()` on the same
                         line in the terminal. (default: {None})
            verbosity {int} -- What verbosity level the command must be running
                               at for the message to be output (default: {1})
        """
        if self.verbosity >= verbosity:
            self.stdout.write(msg, ending=end, style_func=style)
            self.stdout.flush()
