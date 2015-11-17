""""Indigo UI URLs

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


from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView

from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', 'indigo_ui.views.home', name='home'),
    url(r'^archive/', include('archive.urls', namespace="archive")),
    url(r'^node/', include('nodes.urls', namespace="nodes")),
    url(r'^users/', include('users.urls', namespace="users")),
    url(r'^groups/', include('groups.urls', namespace="groups")),
    url(r'^activity/', include('activity.urls', namespace="activity")),

    url(r'^about$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^contact$', TemplateView.as_view(template_name='contact.html'), name='contact'),

    # All routes from here are to be re-routed to the agent by using
    # nginx to re-route calls as an internal redirect
    url(r'^api/cdmi/', include('cdmi.urls', namespace="cdmi")),
    url(r'^api/admin/', include('admin.urls', namespace="admin")),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

