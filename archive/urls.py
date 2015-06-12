from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'archive.views.home', name='home'),
    url(r'^search$', 'archive.views.search', name='search'),
    url(r'^view(?P<path>.*)$', 'archive.views.navigate', name='view'),
    url(r'^resource/(?P<path>.*)$', 'archive.views.resource_view', name='resource_view'),
    url(r'^new/(?P<parent>.*)$', 'archive.views.new', name='new'),
    url(r'^edit/(?P<id>.*)$', 'archive.views.edit', name='edit'),
    url(r'^delete/(?P<id>.*)$', 'archive.views.delete', name='delete'),

    url(r'^download/(?P<path>.*)$', 'archive.views.download', name='download'),
]
