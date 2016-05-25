"""Django settings for Indigo project.

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


    'indigo_ui',
    'archive',
    'activity',
    'nodes',
    'users',
    'groups',
    #'s3',
    'cdmi',
    'admin'
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
    'users.middleware.CassandraAuth',
    'cdmi.middleware.CDMIMiddleware'
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
    "endpoint": "http://127.0.0.1/api/cdmi",
    "username": "",
    "password": "",
}

ADMIN_SERVER = {
    "endpoint": "http://127.0.0.1/api/admin",
}

WSGI_APPLICATION = 'indigo_ui.wsgi.application'

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
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, '../../log/debug.log'),
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'indigo': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'DEBUG'),
        },
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
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
