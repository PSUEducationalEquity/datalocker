from http import cookies
import os


from .models import User


class UserColorHelper():
    #Need to figure out how to use the css combinations here to assign
    #Them to a User for the logged in session
    users = []
    for user in request.get('comment').user:
        users.append(user)

    color_classes = ['azure',
        'black',
        'blue',
        'brown',
        'dark-cyan',
        'dark-magenta',
        'green',
        'hard-cyan',
        'hard-magenta',
        'hard-organe',
        'hard-red',
        'light-grey',
        'maroon',
        'midnight-blue',
        'obscure-grey',
        'obscure-pink',
        'purple',
        'sea-green',
        'slate-grey',
        'tan',
        'yellow',
        'violet-blue',
    ]

    user_color = cookies.SimpleCookie()
    user_color['user_color'] = users
