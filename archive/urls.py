from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'archive.views.home', name='home'),
    url(r'^search$', 'archive.views.search', name='search'),
    url(r'^view/(?P<path>.*)$', 'archive.views.navigate', name='view'),
    url(r'^resource/(?P<id>.*)$', 'archive.views.resource_view', name='resource_view'),
    url(r'^new$', 'archive.views.new', name='new'),
]