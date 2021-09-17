### Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. ###

from django.conf import settings
from django.forms.models import model_to_dict

from random import randint

import logging
import os


logger = logging.getLogger(__name__)


def get_public_user_dict(user):
    """Convert User instance to dict with limited data

    Arguments:
        user {User} -- User instance to convert to a dict

    Returns:
        {dict} -- Dict containing only certain publically-available fields
    """
    public_fields = ['id', 'username', 'email', 'first_name', 'last_name']
    user_dict = {}
    for key, value in model_to_dict(user).iteritems():
        if key in public_fields:
            user_dict[key] = value
    return user_dict


class UserColors():

    AVAILABLE_COLORS = 'user_colors_helper_available_colors'
    ASSIGNMENTS = 'user_colors_helper_color_assignments'
    CSS_FILE = os.path.join(settings.STATIC_ROOT,
                            'datalocker',
                            'css',
                            'user_colors.css')

    def __init__(self, request):
        """Initialize the user colors helper"""
        self.request = request
        self.error = False
        if not self.initialized:
            self.build()

    def _assign(self, username):
        """Assigns and returns an available color to the specified username"""
        try:
            color = self._pop()
        except IndexError:
            color = ''
        self.request.session[self.ASSIGNMENTS][username] = color
        self.request.session.modified = True
        return color

    def build(self):
        """Builds a list of available color classes from the CSS file"""
        available_colors = []
        try:
            with open(self.CSS_FILE, 'r') as css_file:
                for line in css_file:
                    if line[:1] == '.':
                        name = line.split()[0][1:].strip()
                        available_colors.append(name)
        except IOError:
            logger.warning(u"The css file for user colors doesn't exist at the"
                           u" following location '{}'".format(self.CSS_FILE))
            self.error = True
        self.request.session[self.AVAILABLE_COLORS] = available_colors

    def get(self, username):
        """Returns the color for the specified username

        If no color is assigned for this username, one is assigned and then
        returned.
        """
        if self.ASSIGNMENTS not in self.request.session:
            self.request.session[self.ASSIGNMENTS] = {}
        if username in self.request.session[self.ASSIGNMENTS].keys():
            return self.request.session[self.ASSIGNMENTS][username]
        else:
            return self._assign(username)

    @property
    def initialized(self):
        """Boolean indicating if the user colors session list exists"""
        if self.error:
            return False
        if self.AVAILABLE_COLORS not in self.request.session:
            return False
        if len(self.request.session[self.AVAILABLE_COLORS]) == 0:
            return False
        return True

    def _pop(self):
        """Removes a random available color from the list and returns it"""
        try:
            max = len(self.request.session[self.AVAILABLE_COLORS]) - 1
            index = randint(0, max)
        except ValueError:
            color = ''
        else:
            color = self.request.session[self.AVAILABLE_COLORS].pop(index)
            self.request.session.modified = True
        return color
