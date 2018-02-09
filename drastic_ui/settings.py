"""Django settings for Drastic project.
"""
__copyright__ = "Copyright (C) 2016 University of Maryland"
__license__ = "GNU AFFERO GENERAL PUBLIC LICENSE, Version 3"


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '6-_8dk(b%2#=tk6swe2d(ejqy#xh-lj*c=e$1%sz3togm3270('

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False
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


    'drastic_ui',
    'archive',
    'activity',
    'nodes',
    'users',
    'groups',
    #'s3',
    'webdav',
    'cdmi',
    'admin'
)

DEFAULT_APP_CONFIG = 'drastic_ui.DrasticAppConfig'

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
    'users.middleware.CassandraAuth',
    'cdmi.middleware.CDMIMiddleware'
)

ROOT_URLCONF = 'drastic_ui.urls'

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
    "endpoint": "http://127.0.0.1/api/cdmi",
    "username": "",
    "password": "",
}

ADMIN_SERVER = {
    "endpoint": "http://127.0.0.1/api/admin",
}

WSGI_APPLICATION = 'drastic_ui.wsgi.application'

DATABASES = {
#     'test': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/users/login'
#INCLUDE_AUTH_URLS = True
#INCLUDE_REGISTER_URL = True

# LDAP server configuration.
AUTH_LDAP_SERVER_URI = os.getenv('AUTH_LDAP_SERVER_URI', None) # ldap://ldap.example.com
AUTH_LDAP_USER_DN_TEMPLATE = os.getenv('AUTH_LDAP_USER_DN_TEMPLATE', None) # "uid=%(user)s,ou=users,dc=example,dc=com"
# NOTE: AUTHENTICATION_BACKENDS NOT USED, see users/views.py


LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.getenv('DJANGO_STATIC_ROOT', STATIC_ROOT)

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


COMPRESS_UPLOADS = True
DATA_UPLOAD_MAX_MEMORY_SIZE = None


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'filename': os.path.join(BASE_DIR, '../../log/drastic.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True
        },
        'django': {
            'handlers': ['file'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
        },
        'cassandra': {
            'handlers': ['file'],
            'level': 'WARN',
        }
    },
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
#        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ],
#     'DEFAULT_PERMISSION_CLASSES': [
#         'rest_framework.permissions.AllowAny'
    #]
}
#
# REST_SESSION_LOGIN = False
