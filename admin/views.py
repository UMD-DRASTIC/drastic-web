""""Admin views

Copyright 2015 Archive Analytics Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes
)
from rest_framework.authentication import (
    BasicAuthentication,
    exceptions
)
from django.utils.translation import ugettext_lazy as _
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from indigo.models.user import User


 
class CassandraAuthentication(BasicAuthentication):
    www_authenticate_realm = 'Indigo'
 
    def authenticate_credentials(self, userid, password):
        """
        Authenticate the userid and password against username and password.
        """
        user = User.find(userid)
        if user is None or not user.is_active():
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
        if not user.authenticate(password):
            raise exceptions.AuthenticationFailed(_('Invalid username/password.'))
        return (user, None)

@api_view(['GET'])
@authentication_classes((CassandraAuthentication,))
@permission_classes((IsAuthenticated,))
def authenticate(request):
    return Response({"message": "User {} is authenticated".format(request.user.username)})


@api_view(['GET'])
@authentication_classes((CassandraAuthentication,))
def home(request):
    print request.user
    return Response({"message": "Hello for today! See you tomorrow!"})

