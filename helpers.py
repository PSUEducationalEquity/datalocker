import os


from .models import User

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_FILE = os.path.join(BASE_DIR, 'static', 'datalocker', 'css', 'user_colors.css')


class UserColorHelper():
    def list_of_avaiable_colors():
        """
        Searches the css file and assigns all of the classes
        defined into a list for use in a session element
        """
        avail_colors = []
        with open(CSS_FILE, 'r') as cfile:
            for line in cfile:
                if line[:1] == '.':
                    name = line.split()[0][1:]
                    avail_colors.append(name)
        return avail_colors

    def color_user_lookup():
        return ""
