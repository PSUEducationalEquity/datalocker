from django.conf import settings

from random import randint

import logging, os


CSS_FILE = os.path.join(settings.STATIC_ROOT, 'datalocker', 'css', 'user_colors.css')
COLOR_HELPER_AVAILABLE_COLORS = 'user_colors_helper_available_colors'
COLOR_HELPER_ASSIGNMENTS = 'user_colors_helper_color_assignments'

logger = logging.getLogger(__name__)


class UserColors():
    def __init__(self, request):
        """
        Initialize the user colors helper
        """
        self.request = request
        self.error = False
        if not self.initialized:
            self.build()


    def _assign(self, username):
        """
        Assigns an available color to the specified username and returns it
        """
        try:
            color = self._pop()
        except IndexError:
            color = ''
        self.request.session[COLOR_HELPER_ASSIGNMENTS][username] = color
        self.request.session.modified = True
        return color


    def build(self):
        """
        Builds a list of available color classes from the CSS file
        """
        available_colors = []
        try:
            with open(CSS_FILE, 'r') as css_file:
                for line in css_file:
                    if line[:1] == '.':
                        name = line.split()[0][1:].strip()
                        available_colors.append(name)
        except IOError:
            logger.warning("The css file for user colors doesn't exist at " \
            "the following location '%s'" % CSS_FILE)
            self.error = True
        self.request.session[COLOR_HELPER_AVAILABLE_COLORS] = available_colors


    def get(self, username):
        """
        Returns the color for the specified username, assigning a new color
        if one doesn't already exist
        """
        if COLOR_HELPER_ASSIGNMENTS not in self.request.session:
            self.request.session[COLOR_HELPER_ASSIGNMENTS] = {}
        if username in self.request.session[COLOR_HELPER_ASSIGNMENTS].keys():
            return self.request.session[COLOR_HELPER_ASSIGNMENTS][username]
        else:
            return self._assign(username)


    @property
    def initialized(self):
        """
        Boolean indicating if the user colors session list exists
        """
        if not self.error \
        and COLOR_HELPER_AVAILABLE_COLORS in self.request.session \
        and len(self.request.session[COLOR_HELPER_AVAILABLE_COLORS]) > 0:
            return True
        return False


    def _pop(self):
        """
        Pops a random available color from the list and returns it
        """
        try:
            index = randint(
                0,
                len(self.request.session[COLOR_HELPER_AVAILABLE_COLORS]) - 1
            )
        except ValueError:
            color = ''
        else:
            color = self.request.session[COLOR_HELPER_AVAILABLE_COLORS].pop(index)
            self.request.session.modified = True
        return color
