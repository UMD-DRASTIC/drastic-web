"""Archive URLs

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

from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'archive.views.home', name='home'),
    url(r'^search$', 'archive.views.search', name='search'),
    url(r'^search2$', 'archive.views.search2', name='search2'),

    url(r'^resource(?P<path>.*)$', 'archive.views.view_resource', name='resource_view'),
    url(r'^new/collection(?P<parent>.*)$', 'archive.views.new_collection', name='new_collection'),
    url(r'^edit/collection(?P<path>.*)$', 'archive.views.edit_collection', name='edit_collection'),
    url(r'^delete/collection(?P<path>.*)$', 'archive.views.delete_collection', name='delete_collection'),

    url(r'^new/resource(?P<parent>.*)$', 'archive.views.new_resource', name='new_resource'),
    url(r'^edit/resource(?P<path>.*)$', 'archive.views.edit_resource', name='edit_resource'),
    url(r'^delete/resource(?P<path>.*)$', 'archive.views.delete_resource', name='delete_resource'),

    url(r'^view(?P<path>.*)$', 'archive.views.view_collection', name='view'),
    url(r'^download(?P<path>.*)$', 'archive.views.download', name='download'),
    url(r'^preview(?P<path>.*)$', 'archive.views.preview', name='preview'),
]
