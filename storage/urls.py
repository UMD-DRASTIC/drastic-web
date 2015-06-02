from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'storage.views.home', name='home'),
    url(r'^new$', 'storage.views.new', name='new'),
    url(r'^(?P<name>.*)/edit$', 'storage.views.modify', name='modify'),
]
