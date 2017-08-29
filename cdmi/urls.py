""""CDMI URLs

"""
from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from cdmi.views import (
    capabilities,
    crud_id,
    CDMIView
)

__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"

urlpatterns = [
   url(r'^cdmi_capabilities(?P<path>.*)$', capabilities, name='capabilities'),
   url(r'^cdmi_objectid/(?P<id>.*)$', crud_id, name='crud_id'),

   url(r'^(?P<path>.*)$', CDMIView.as_view(), name="api_cdmi"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
