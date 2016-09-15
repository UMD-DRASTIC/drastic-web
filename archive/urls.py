"""Archive URLs

"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


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
