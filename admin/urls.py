""""Admin URLs

"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from django.conf.urls import (
    url,
    include
)
from rest_framework.urlpatterns import format_suffix_patterns


from . import views

urlpatterns = [
   url(r'^authenticate$', views.authenticate),
   url(r'^users/(?P<username>.*)', views.user),
   url(r'^users', views.users),
   url(r'^groups/(?P<groupname>.*)', views.group),
   url(r'^groups', views.groups),
   url(r'^$', views.home),
   
]


urlpatterns = format_suffix_patterns(urlpatterns)
