""""Admin URLs

"""
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from views import authenticate, user, users, group, groups, home

__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"

urlpatterns = [
   url(r'^authenticate$', authenticate),
   url(r'^users/(?P<username>.*)', user),
   url(r'^users', users),
   url(r'^groups/(?P<groupname>.*)', group),
   url(r'^groups', groups),
   url(r'^$', home),

]


urlpatterns = format_suffix_patterns(urlpatterns)
