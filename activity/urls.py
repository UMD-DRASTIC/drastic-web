"""Activity URLs
"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


from django.conf.urls import url
from activity.views import home

urlpatterns = [
    url(r'^$', home, name='home'),
]
