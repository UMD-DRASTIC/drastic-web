""""Users UI URLs
"""

from django.conf.urls import url
from users.views import (
    home,
    userlogin,
    userlogout,
    new_user,
    delete_user,
    edit_user,
    user_view
)
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^login$', userlogin, name='auth_login'),
    url(r'^logout$', userlogout, name='auth_logout'),

    url(r'^new/user$', new_user, name='new_user'),
    url(r'^delete/user/(?P<name>.*)$', delete_user, name='delete_user'),
    url(r'^edit/user/(?P<name>.*)$', edit_user, name='edit_user'),

    url(r'^(?P<name>.*)$', user_view, name='view'),


]
