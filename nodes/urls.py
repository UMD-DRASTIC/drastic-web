"""Node URLs
"""
from django.conf.urls import url
from nodes.views import (
    home,
    new,
    edit,
    check,
    logview,
    metrics
)
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"

urlpatterns = [
    url(r'^$', home, name='home'),
    url(r'^new$', new, name='new'),
    url(r'^(?P<id>.*)/edit$', edit, name='edit'),
    url(r'^(?P<id>.*)/check$', check, name='check'),
    url(r'^(?P<id>.*)/log$', logview, name='logview'),
    url(r'^(?P<id>.*)/metrics$', metrics, name='metrics'),
]
