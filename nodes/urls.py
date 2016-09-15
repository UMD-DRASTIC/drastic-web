"""Node URLs
"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from django.conf.urls import url

urlpatterns = [
    url(r'^$', 'nodes.views.home', name='home'),
    url(r'^new$', 'nodes.views.new', name='new'),
    url(r'^(?P<id>.*)/edit$', 'nodes.views.edit', name='edit'),
    url(r'^(?P<id>.*)/check$', 'nodes.views.check', name='check'),
    url(r'^(?P<id>.*)/log$', 'nodes.views.logview', name='logview'),
    url(r'^(?P<id>.*)/metrics$', 'nodes.views.metrics', name='metrics'),
]
