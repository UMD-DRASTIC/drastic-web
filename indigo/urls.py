from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView

from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', 'indigo.views.home', name='home'),
    url(r'^archive/', include('archive.urls', namespace="archive")),
    url(r'^storage/', include('storage.urls', namespace="storage")),
    url(r'^users/', include('users.urls', namespace="users")),
    url(r'^activity/', include('activity.urls', namespace="activity")),

    url(r'^about$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^contact$', TemplateView.as_view(template_name='contact.html'), name='contact'),

    url(r'^accounts/', include('registration.backends.default.urls')),

    url(r'^admin/', include(admin.site.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Indigo Administration'