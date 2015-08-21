import logging, os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_FILE = os.path.join(BASE_DIR, 'static', 'datalocker', 'css', 'user_colors.css')

logger = logging.getLogger(__name__)

class UserColorHelper():
    def list_of_avaiable_colors():
        """
        Searches the css file and assigns all of the classes
        defined into a list for use in a session element
        """
        avail_colors = []
        try:
            with open(CSS_FILE, 'r') as cfile:
                for line in cfile:
                    if line[:1] == '.':
                        name = line.split()[0][1:]
                        avail_colors.append(name)
        except:
            logger.warning("The css file for user colors doesn't exist at " \
            "the following location '%s'" % CSS_FILE)
        return avail_colors

    def color_user_lookup():
        avail_colors = list_of_avaiable_colors()
        users = []
        return ""
