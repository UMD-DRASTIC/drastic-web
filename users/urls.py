""""Users UI URLs
"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'users.views.home', name='home'),
    url(r'^login$', 'users.views.userlogin', name='auth_login'),
    url(r'^logout$', 'users.views.userlogout', name='auth_logout'),
    
    url(r'^new/user$', 'users.views.new_user', name='new_user'),
    url(r'^delete/user/(?P<name>.*)$', 'users.views.delete_user', name='delete_user'),
    url(r'^edit/user/(?P<name>.*)$', 'users.views.edit_user', name='edit_user'),
    
    url(r'^(?P<name>.*)$', 'users.views.user_view', name='view'),
    

]
