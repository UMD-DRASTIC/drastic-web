""""CDMI URLs

"""

from django.conf.urls import (
    url
)
from rest_framework.urlpatterns import format_suffix_patterns
from djangodav.acls import FullAcl
from djangodav.locks import DummyLock
from views import DrasticDavView
from resources import DrasticDavResource
# from views import RestAuthDavView


__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


urlpatterns = [
   url(r'^(?P<path>.*)$', DrasticDavView.as_view(resource_class=DrasticDavResource,
       lock_class=DummyLock, acl_class=FullAcl))
]

urlpatterns = format_suffix_patterns(urlpatterns)
