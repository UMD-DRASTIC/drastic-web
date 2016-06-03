from django.core.cache import cache

class CassandraAuth(object):

    def process_request(self, request):
        from indigo.models import User

        username = request.session.get('user')
        if not username:
            return None

        # Cache the user rather than hitting the database for
        # each request.  We can also invalidate the entry if the
        # user is marked as inactive.
        user = cache.get('user_{}'.format(username), None)
        if not user:
            user = User.find(username)
        request.user = user
        cache.set('user_{}'.format(username), user, 60)

        return None