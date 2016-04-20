from django.core.cache import cache

class CassandraAuth(object):

    def process_request(self, request):
        from indigo.models import User

        user_uuid = request.session.get('user')
        if not user_uuid:
            return None

        # Cache the user rather than hitting the database for
        # each request.  We can also invalidate the entry if the
        # user is marked as inactive.
        user = cache.get('user_{}'.format(user_uuid), None)
        if not user:
            user = User.find_by_uuid(user_uuid)
        request.user = user
        cache.set('user_{}'.format(user_uuid), user, 60)

        return None