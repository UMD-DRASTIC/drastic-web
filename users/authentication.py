
from indigo.models import User


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
