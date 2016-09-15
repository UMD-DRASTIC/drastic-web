""""CDMI URLs

"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from django.conf.urls import (
    url,
    include
)
from rest_framework.urlpatterns import format_suffix_patterns
from cdmi import views


urlpatterns = [
   url(r'^cdmi_capabilities(?P<path>.*)$', 'cdmi.views.capabilities', name='capabilities'),
   url(r'^cdmi_objectid/(?P<id>.*)$', 'cdmi.views.crud_id', name='crud_id'),
   
   url(r'^(?P<path>.*)$', views.CDMIView.as_view(), name="api_cdmi"),
]

urlpatterns = format_suffix_patterns(urlpatterns)

