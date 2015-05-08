from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'activity.views.home', name='home'),
]
