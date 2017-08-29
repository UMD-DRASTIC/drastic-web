"""Archive URLs

"""

from archive.views import (
    home,
    search,
    search2,
    view_resource,
    new_collection,
    edit_resource,
    edit_collection,
    delete_resource,
    delete_collection,
    new_resource,
    view_collection,
    download,
    preview
)
from django.conf.urls import url

__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^search$', search, name='search'),
    url(r'^search2$', search2, name='search2'),

    url(r'^resource(?P<path>.*)$', view_resource, name='resource_view'),
    url(r'^new/collection(?P<parent>.*)$', new_collection, name='new_collection'),
    url(r'^edit/collection(?P<path>.*)$', edit_collection, name='edit_collection'),
    url(r'^delete/collection(?P<path>.*)$', delete_collection, name='delete_collection'),

    url(r'^new/resource(?P<parent>.*)$', new_resource, name='new_resource'),
    url(r'^edit/resource(?P<path>.*)$', edit_resource, name='edit_resource'),
    url(r'^delete/resource(?P<path>.*)$', delete_resource, name='delete_resource'),

    url(r'^view(?P<path>.*)$', view_collection, name='view'),
    url(r'^download(?P<path>.*)$', download, name='download'),
    url(r'^preview(?P<path>.*)$', preview, name='preview'),
]
