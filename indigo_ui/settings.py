"""
Django settings for Indigo project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6-_8dk(b%2#=tk6swe2d(ejqy#xh-lj*c=e$1%sz3togm3270('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = []

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = (
    'flat',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'django_extensions',
    'rest_framework',
    'django_gravatar',


    'indigo_ui',
    'archive',
    'activity',
    'nodes',
    'users',
    'router'
)

DEFAULT_APP_CONFIG = 'indigo_ui.IndigoAppConfig'

SITE_ID = 1

FILE_UPLOAD_HANDLERS = ("archive.uploader.AgentUploader",)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'users.middleware.CassandraAuth'
)

ROOT_URLCONF = 'indigo_ui.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CDMI_SERVER = {
    "endpoint": "http://127.0.0.1:8001/cdmi",
    "username": "",
    "password": "",
}

WSGI_APPLICATION = 'indigo_ui.wsgi.application'

DATABASES = {
    'test': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'indigo',
        'HOST': '127.0.0.1',
        'USER': 'indigo',
        'PASS': 'indigo'
    },
}

LOGIN_REDIRECT_URL = '/'
#INCLUDE_AUTH_URLS = True
#INCLUDE_REGISTER_URL = True

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Try and load a local, machine specific settings if it exists.
try:
    from local_settings import *
except:
    pass

##############################################################################
# Caching
##############################################################################
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


##############################################################################
# Initialise the database connection
# TODO: Move this somewhere more useful!
##############################################################################
from indigo.models import initialise, Collection
initialise("indigo")
root = Collection.get_root_collection()
if not root:
    print "Creating root collection"
    Collection.create(name="Home", path="/")
else:
    print "Using existing root collection"



LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'indigo': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
    },
}