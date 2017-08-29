""""Groups UI URLs

"""
from django.conf.urls import url
from groups.views import (
    home,
    new_group,
    delete_group,
    edit_group,
    rm_user,
    add_user,
    group_view
)
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"

urlpatterns = [
    url(r'^$', home, name='home'),

    url(r'^new/group', new_group, name='new_group'),
    url(r'^delete/group/(?P<name>.*)$', delete_group, name='delete_group'),
    url(r'^edit/group/(?P<name>.*)$', edit_group, name='edit_group'),

    url(r'^rm/(?P<name>.*)/(?P<uname>.*)$', rm_user, name='rm_user'),
    url(r'^add/(?P<name>.*)$', add_user, name='add_user'),

    url(r'^(?P<name>.*)$', group_view, name='view'),
]
