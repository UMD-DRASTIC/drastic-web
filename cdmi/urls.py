from django.conf.urls import url

urlpatterns = [
    url(r'^cdmi_capabilities(?P<path>.*)$', 'cdmi.views.capabilities', name='capabilities'),
]
