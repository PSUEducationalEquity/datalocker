import os


from .models import User

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_FILE = os.path.join(BASE_DIR, 'static', 'datalocker', 'css', 'user_colors.css')


class UserColorHelper():
    #Need to figure out how to use the css combinations here to assign
    #Them to a User for the logged in session
    def list_of_avaiable_colors():
        with open(CSS_FILE, 'r') as file:
            for line in file:
                print line

        avail_colors = []

    def color_user_lookup():
        return ""
