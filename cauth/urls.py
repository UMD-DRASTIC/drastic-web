from django.conf.urls import url

urlpatterns = [
    url(r'^login$', 'cauth.views.login_view', name='login'),
    url(r'^logout$', 'cauth.views.logout_view', name='logout'),
]
