

class CassandraAuth(object):

    def process_request(self, request):
        from indigo.models import User

        user_id = request.session.get('user')
        if not user_id:
            return None

        request.user = User.find_by_id(user_id)

        return None