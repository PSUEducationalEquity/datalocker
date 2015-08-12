#started a helpers.py file, not sure what to put into here yet.
from .models import User


class UserColorHelper():
    #Need to figure out how to use the css combinations here to assign
    #Them to a User for the logged in session
    user = request.POST.get('user')

