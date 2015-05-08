from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'storage.views.home', name='home'),
]
