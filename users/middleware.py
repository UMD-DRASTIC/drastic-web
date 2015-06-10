from django.core.cache import cache

class CassandraAuth(object):

    def process_request(self, request):
        from indigo.models import User

        user_id = request.session.get('user')
        if not user_id:
            return None

        # Cache the user rather than hitting the database for
        # each request.  We can also invalidate the entry if the
        # user is marked as inactive.
        user = cache.get('user_{}'.format(user_id), None)
        if not user:
            user = User.find_by_id(user_id)
        request.user = user
        cache.set('user_{}'.format(user_id), user, 60)

        return None