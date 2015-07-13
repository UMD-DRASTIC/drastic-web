from django.conf.urls import url

urlpatterns = [
    url(r'^cdmi_capabilities/$', 'cdmi.views.capabilities', name='capabilities'),
]
