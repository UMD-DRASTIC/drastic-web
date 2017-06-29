""""Drastic UI URLs
"""

from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView

from django.conf.urls.static import static


__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"

urlpatterns = [
    url(r'^$', 'drastic_ui.views.home', name='home'),
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
    url(r'^api/webdav/', include('webdav.urls', namespace="webdav")),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
