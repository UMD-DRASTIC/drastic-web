from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'users.views.home', name='home'),
]
