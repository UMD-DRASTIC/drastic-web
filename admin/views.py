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
import json
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_206_PARTIAL_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT
)
import ldap

from indigo.models.group import Group
from indigo.models.user import User
from django.conf import settings

class CassandraAuthentication(BasicAuthentication):
    www_authenticate_realm = 'Indigo'

    def authenticate_credentials(self, username, password):
        """
        Authenticate the userid and password against username and password.
        """
        user = User.find(username)
        if user is None or not user.is_active():
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))
        if not user.authenticate(password) and not ldapAuthenticate(userid, password):
            raise exceptions.AuthenticationFailed(_('Invalid username/password.'))
        return (user, None)

def ldapAuthenticate(username, password):
    if settings.AUTH_LDAP_SERVER_URI is None:
        return False

    if settings.AUTH_LDAP_USER_DN_TEMPLATE is None:
        return False

    try:
        connection = ldap.initialize(settings.AUTH_LDAP_SERVER_URI)
        connection.protocol_version = ldap.VERSION3
        user_dn = settings.AUTH_LDAP_USER_DN_TEMPLATE % {"user": username}
        connection.simple_bind_s(user_dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except ldap.SERVER_DOWN:
        return False


@api_view(['GET'])
@authentication_classes((CassandraAuthentication,))
@permission_classes((IsAuthenticated,))
def authenticate(request):
    msg = u"User {} is authenticated".format(request.user.name)
    return Response({"message": msg})


@api_view(['GET', 'DELETE', 'PUT'])
@authentication_classes((CassandraAuthentication,))
@permission_classes((IsAuthenticated,))
def group(request, groupname):
    if request.method == 'GET':
        return ls_group(request, groupname)
    elif request.method == 'DELETE':
        if request.user and request.user.administrator:
            return delete_group(request, groupname)
        else:
            return Response("User lack authorization.",
                            status=HTTP_403_FORBIDDEN)
    elif request.method == 'PUT':
        if request.user and request.user.administrator:
            return modify_group(request, groupname)
        else:
            return Response("User lack authorization.",
                            status=HTTP_403_FORBIDDEN)


@api_view(['GET', 'POST'])
@authentication_classes((CassandraAuthentication,))
@permission_classes((IsAuthenticated,))
def groups(request):
    if request.method == 'GET':
        return Response([u.name for u in Group.objects.all()])
    elif request.method == 'POST':
        if request.user and request.user.administrator:
            return create_group(request)
        else:
            return Response("User lack authorization.",
                            status=HTTP_403_FORBIDDEN)


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes((CassandraAuthentication,))
@permission_classes((IsAuthenticated,))
def user(request, username):
    if request.method == 'GET':
        return ls_user(request, username)
    elif request.method == 'PUT':
        if request.user and request.user.administrator:
            return modify_user(request, username)
        else:
            return Response("User lack authorization.",
                            status=HTTP_403_FORBIDDEN)
    elif request.method == 'DELETE':
        if request.user and request.user.administrator:
            return delete_user(request, username)
        else:
            return Response("User lack authorization.",
                            status=HTTP_403_FORBIDDEN)


def create_group(request):
    """Expecting json in the body:
    { "username": username,
      "groupname": groupname }
    """
    try:
        body = request.body
        request_body = json.loads(body)
    except:
        return Response("Invalid JSON body", status=HTTP_400_BAD_REQUEST)
    try:
        groupname = request_body['groupname']
    except KeyError:
        return Response("Missing groupname", status=HTTP_400_BAD_REQUEST)
    group = Group.find(groupname)
    if group:
        return Response("Group already exists", status=HTTP_409_CONFLICT)
    group = Group.create(name=groupname)
    return Response(group.to_dict(), status=HTTP_201_CREATED)


def create_user(request):
    """Expecting json in the body:
    { "username": username,
      "password": password,
      "email": email,
      "administrator": is_admin }
    """
    try:
        body = request.body
        request_body = json.loads(body)
    except:
        return Response("Invalid JSON body", status=HTTP_400_BAD_REQUEST)
    try:
        username = request_body['username']
    except KeyError:
        return Response("Missing username", status=HTTP_400_BAD_REQUEST)
    user = User.find(username)
    if user:
        return Response("User already exists", status=HTTP_409_CONFLICT)
    try:
        email = request_body['email']
    except KeyError:
        return Response("Missing email", status=HTTP_400_BAD_REQUEST)
    try:
        password = request_body['password']
    except KeyError:
        return Response("Missing password", status=HTTP_400_BAD_REQUEST)
    administrator = request_body.get('administrator', False)
    user = User.create(name=username,
                       password=password,
                       email=email,
                       administrator=administrator)
    return Response(user.to_dict(), status=HTTP_201_CREATED)


def delete_group(request, groupname):
    """Delete a group"""
    group = Group.find(groupname)
    if not group:
        return Response(u"Group {} doesn't exists".format(groupname),
                        status=HTTP_404_NOT_FOUND)
    group.delete()
    return Response(u"Group {} has been deleted".format(groupname),
                    status=HTTP_200_OK)


def delete_user(request, username):
    """Delete a user"""
    user = User.find(username)
    if not user:
        return Response(u"User {} doesn't exists".format(username),
                        status=HTTP_404_NOT_FOUND)
    user.delete()
    return Response(u"User {} has been deleted".format(username),
                    status=HTTP_200_OK)


def add_user_group(group, ls_users):
    # Check that all users exists
    added, not_added, already_there = group.add_users(ls_users)
    msg = []

    if added:
        msg.append(u"Added {} to the group {}".format(
            ", ".join(added),
            group.name))
    if already_there:
        if len(already_there) == 1:
            verb = "is"
        else:
            verb = "are"
        msg.append(u"{} {} already in the group {}".format(
            ", ".join(already_there),
            verb,
            group.name))
    if not_added:
        msg.append(u"{} doesn't exist".format(", ".join(not_added)))
    msg = ", ".join(msg)
    if not_added or already_there:
        return Response(msg, status=HTTP_206_PARTIAL_CONTENT)
    else:
        return Response(msg, status=HTTP_200_OK)


def rm_user_group(group, ls_users):
    removed, not_there, not_exist = group.rm_users(ls_users)
    msg = []

    if removed:
        msg.append(u"Removed {} from the group {}".format(", ".join(removed),
                                                         group.name))
    if not_there:
        if len(not_there) == 1:
            verb = "isn't"
        else:
            verb = "aren't"
        msg.append(u"{} {} in the group {}".format(", ".join(not_there),
                                                  verb,
                                                  group.name))
    if not_exist:
        msg.append(u"{} doesn't exist".format(", ".join(not_exist)))
    msg = ", ".join(msg)
    if not_there or not_exist:
        return Response(msg, status=HTTP_206_PARTIAL_CONTENT)
    else:
        return Response(msg, status=HTTP_200_OK)


def modify_group(request, groupname):
    """Expecting json in the body:
    { "groupname": groupname, # Optional
      "add_users": [user1, user2, ...],
      "rm_users": [user1, user2, ...]
    }
    """
    try:
        body = request.body
        request_body = json.loads(body)
    except:
        return Response("Invalid JSON body", status=HTTP_400_BAD_REQUEST)
    group = Group.find(groupname)
    if not group:
        return Response(u"Group {} doesn't exists".format(groupname),
                        status=HTTP_404_NOT_FOUND)

    # Add users to group
    if 'add_users' in request_body:
        return add_user_group(group, request_body['add_users'])
    # Remove users from group
    if 'rm_users' in request_body:
        return rm_user_group(group, request_body['rm_users'])


def ls_group(request, groupname):
    # TODO check if groupname is valid to test ?
    group = Group.find(groupname)
    try:
        return Response(group.to_dict())
    except:
        return Response(u"Group {} not found".format(groupname),
                        status=HTTP_404_NOT_FOUND)


def modify_user(request, username=""):
    """Expecting json in the body:
    { "username": username,
      "password": password,
      "email": email,
      "administrator": is_admin,
      "active": is_active}
    """
    try:
        body = request.body
        request_body = json.loads(body)
    except:
        return Response("Invalid JSON body", status=HTTP_400_BAD_REQUEST)
    if username is None:
        try:
            username = request_body['username']
        except KeyError:
            return Response("Missing username", status=HTTP_400_BAD_REQUEST)
    user = User.find(username)
    if not user:
        return Response(u"User {} doesn't exists".format(username),
                        status=HTTP_404_NOT_FOUND)
    if 'email' in request_body:
        user.update(email=request_body['email'])
    if 'password' in request_body:
        user.update(password=request_body['password'])
    if 'administrator' in request_body:
        user.update(administrator=request_body['administrator'])
    if 'active' in request_body:
        user.update(active=request_body['active'])
    return Response(user.to_dict(), status=HTTP_200_OK)


def ls_user(request, username):
    # TODO check if username is valid to test ?
    user = User.find(username)
    if user:
        return Response(user.to_dict(), status=HTTP_200_OK)
    else:
        return Response(u"User {} not found".format(username),
                        status=HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@authentication_classes((CassandraAuthentication,))
@permission_classes((IsAuthenticated,))
def users(request):
    if request.method == 'GET':
        return Response([u.name for u in User.objects.all()])
    elif request.method == 'POST':
        return create_user(request)


@api_view(['GET'])
@authentication_classes((CassandraAuthentication,))
def home(request):
    return Response({"message": "Hello for today! See you tomorrow!"})
