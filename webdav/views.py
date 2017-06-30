from djangodav.views import DavView
from djangodav.acls import FullAcl
from djangodav.auth.rest import RestAuthViewMixIn
from cdmi.views import CassandraAuthentication
from django.conf import settings
from rest_framework.authentication import (
    BasicAuthentication,
    exceptions
)
from drastic.models import (
    User,
    Collection
)
import ldap
import logging


class DrasticDavView(RestAuthViewMixIn, DavView):
    authentications = (CassandraAuthentication(),)

    def get_access(self, resource):
        """Return permission as DavAcl object. A DavACL should have the following attributes:
        read, write, delete, create, relocate, list. By default we implement a read-only
        system."""
        user = self.request.user
        if resource.me() is None:
            container = None
            if resource.get_parent_path() == '' or resource.get_parent_path() == '/':
                container = '/'
            else:
                container = resource.get_parent_path()[:-1]
            parent_collection = Collection.find(container)
            if parent_collection.user_can(user, "write"):
                acl = FullAcl(read=False, write=True, delete=False)
            else:
                acl = FullAcl(full=False)
        else:
            delete = resource.me().user_can(user, "delete")
            read = resource.me().user_can(user, "read")
        # full = resource.me().user_can(self.user, "create")
            write = resource.me().user_can(user, "write")
            acl = FullAcl(read=read, write=write, delete=delete)

        # return self.acl_class(read=True, full=False)  Old permissive code
        return acl


class CassandraAuthentication(BasicAuthentication):
    www_authenticate_realm = 'Drastic'

    def authenticate_credentials(self, username, password):
        """
        Authenticate the username and password against username and password.
        """
        user = User.find(username)
        if user is None or not user.is_active():
            raise exceptions.AuthenticationFailed('User inactive or deleted.')
        if not user.authenticate(password) and not ldapAuthenticate(username, password):
            raise exceptions.AuthenticationFailed('Invalid username/password.')
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
