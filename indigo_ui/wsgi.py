"""
WSGI config for Indigo project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "indigo_ui.settings")

application = get_wsgi_application()
