
from indigo.models import User

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test

def administrator_required(function=None,
                           redirect_field_name=REDIRECT_FIELD_NAME,
                           login_url=None):
    """
    Decorator for views that checks that the user is logged in and an
    administrator
    """
    actual_decorator = user_passes_test(
        lambda u: u.administrator,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

class Backend(object):

    def get_user(self, id):
        return User.find(username)

    def authenticate(self, username=None, password=None):
        user = User.find(username)
        if not user:
            print "User not found"
            return None
        if not user.authenticate(password):
            print "User not authenticated"
            return None
        return user
