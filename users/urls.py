""""Users UI URLs

Copyright 2015 Archive Analytics Solutions

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

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
