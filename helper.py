"""File containing helper functions needed by the application."""
from dbconnect import connection   # for connecting with database
from functools import wraps        # for creating wrapper function
from flask import render_template, session


def is_username_exist(username):
    """To check wether username already exists or not."""
    c, conn = connection()              # establishing connection
    count = c.execute("SELECT * FROM users WHERE username = (%s)",
                      (username))  # running query to find out number of users
    return count


def login_required(f):
    """Wrapper that checks wether user is in session and helps protect certain \
    pages."""
    @wraps(f)  # f symbolizes function
    def wrap(*args, **kwargs):

        if 'logged_in' in session:   # checking wether user is in session
            return f(*args, **kwargs)
        else:
            return render_template('UserAccount/login.html',  # return to login page if user not in session
                                   message='please login first')
    return wrap
