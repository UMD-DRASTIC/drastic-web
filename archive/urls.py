from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'archive.views.home', name='home'),
    url(r'^search$', 'archive.views.search', name='search'),

    url(r'^resource/(?P<id>.*)$', 'archive.views.resource_view', name='resource_view'),
    url(r'^new/collection/(?P<parent>.*)$', 'archive.views.new_collection', name='new_collection'),
    url(r'^edit/collection/(?P<id>.*)$', 'archive.views.edit_collection', name='edit_collection'),
    url(r'^delete/collection/(?P<id>.*)$', 'archive.views.delete_collection', name='delete_collection'),

    url(r'^new/resource/(?P<container>.*)$', 'archive.views.new_resource', name='new_resource'),
    url(r'^edit/resource/(?P<id>.*)$', 'archive.views.edit_resource', name='edit_resource'),
    url(r'^delete/resource/(?P<id>.*)$', 'archive.views.delete_resource', name='delete_resource'),

    url(r'^view(?P<path>.*)$', 'archive.views.navigate', name='view'),
    url(r'^download/(?P<path>.*)$', 'archive.views.download', name='download'),
]
