from django.conf import settings
from django.conf.urls import include, url
from django.views.generic import TemplateView

from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', 'indigo_ui.views.home', name='home'),
    url(r'^archive/', include('archive.urls', namespace="archive")),
    url(r'^node/', include('nodes.urls', namespace="nodes")),
    url(r'^users/', include('users.urls', namespace="users")),
    url(r'^activity/', include('activity.urls', namespace="activity")),

    url(r'^about$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^contact$', TemplateView.as_view(template_name='contact.html'), name='contact'),

    # All routes from here are to be re-routed to the agent by using
    # nginx to re-route calls as an internal redirect
    url(r'^cdmi/', include('cdmi.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

