from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'users.views.home', name='home'),
    url(r'^login$', 'users.views.userlogin', name='auth_login'),
    url(r'^logout$', 'users.views.userlogout', name='auth_logout'),
    url(r'^(?P<id>.*)$', 'users.views.user_view', name='view'),

]
