from django.conf.urls import url

urlpatterns = [
    url(r'^(?P<path>.*)$', 'router.views.route', name='route'),
]
