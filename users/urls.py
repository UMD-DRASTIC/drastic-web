from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'users.views.home', name='home'),
    url(r'^(?P<id>.*)$', 'users.views.user_view', name='view'),
]
