#
# Django settings for WarMist project.
import os,sys
#from apps import djcelery
#djcelery.setup_loader()

ADMINS = (
    ('Saul Tarvitz', 'tarvitz@blacklibrary.ru'),
)

def get_local(value, default):
    import local
    if hasattr(local, value):
        return getattr(local, value)
    return default

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'

SITE_ID = 1

_ = lambda s: s
LANGUAGES = (
    ('ru', _('Russian')),
    ('en', _('English')),
)
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

from settings_path import rel_path

MEDIA_ROOT=get_local('MEDIA_ROOT', rel_path('media'))
STYLES_ROOT = rel_path('styles')
ADMIN_MEDIA = rel_path('admin_media')
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

STATIC_ROOT = rel_path('media/static')

#STATICFILES_DIRS = (
#    rel_path('media'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
#)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    #deprecated
    #'django.template.loaders.filesystem.load_template_source',
    #'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'apps.core.middleware.ChecksMiddleware',
    'apps.core.middleware.UserActivityMiddleware',
    'apps.core.middleware.GuestActivityMiddleware',
    'apps.core.middleware.TestMiddleware',
    #obsolete
    #'apps.core.middleware.UserSettingsMiddleware',
    'apps.wh.middleware.WarningsMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    #deprecated
    #'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'apps.core.context_processors.global_settings',
    'apps.core.context_processors.expressions',
    'apps.core.context_processors.briefing_news',
    'apps.core.context_processors.last_replays',
    'apps.core.context_processors.pm',
    'apps.core.context_processors.user_settings',
    'apps.core.context_processors.global_referer',
    'apps.core.context_processors.base_template',
    'apps.core.context_processors.session',
    'apps.farseer.context_processors.steam_discounts',
)
TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
    rel_path('templates'),
)
#FILE_UPLOAD_HANDLERS = (
#    "apps.core.handlers.UploadProgressHandler",
#    "django.core.files.uploadhandler.MemoryFileUploadHandler",
#    "django.core.files.uploadhandler.TemporaryFileUploadHandler",
#)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apps.files':{
            'level': "INFO",
            'propagate': True,
            'handlers': ['console',],
        },
        'apps.core':{
            'level': 'INFO',
            'propagate': True,
            'handlers': ['console',],
        },
        'apps.farseer':{
            'level': 'INFO',
            'propagate': True,
            'handlers': ['console',],
        },
        'apps.thirdpaty.sleekxmpp.basexmpp':{
            'level': 'INFO',
            'propagate': True,
            'handlers': ['console',],
        },
        'apps.thirdpaty.sleekxmpp.xmlstream.xmlstream':{
            'level': 'INFO',
            'propagate': True,
            'handlers': ['console',],
        },
    },

}

INSTALLED_APPS = (
    'django.contrib.sitemaps',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.comments',
    'django.contrib.flatpages',
    'django.contrib.staticfiles',
    #
    'apps.jsonapp',
    'apps.core',
    'apps.wh',
    'apps.whadmin',
    'apps.news',
    'apps.files',
    'apps.tabletop',
    #'apps.quotes', # conflicts with grappelli
    'apps.vote',
    'apps.tagging',
    'utils',
    #'apps.bincase',
    'apps.karma',
    'apps.blogs',
    'apps.tracker',
    'apps.farseer',
    'apps.pybb',
    'djcelery',
    'apps.djangosphinx',
    'extwidgets',
    'south',
    'sorl.thumbnail',
    #
    'grappelli',
    'django.contrib.admin',
    'django.contrib.admindocs',
)
#settings
APP_VOTE_ENABLED=True
PRODUCTION=get_local('PRODUCTION', True)
DEVELOPMENT=get_local('DEVELOPMENT', False)
YANDEX_METRICA_ENABLED = get_local('YANDEX_METRICA_ENABLED', False)
ENABLE_500_TEST=False
SERVER_EMAIL='noreply@w40k.net'
DEV_SERVER=True
GRAPPELLI_ADMIN_TITLE='w40k.net'
USE_OLD_THUMBNAIL_IMAGE_SCHEME=False
DEFAULT_TEMPLATE='base.html'
DEFAULT_SYNTAX='textile'
IMAGE_THUMBNAIL_SIZE='200x200'

#import settings from another app
# LOGGING

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apps.sms': {
            'handlers': ['console',],
            'level': 'INFO',
            'propagate': True
        },
        'apps.repspot': {
            'handlers': ['console', ],
            'level': 'INFO',
            'propagate': True
        },
        'apps.bands': {
            'handlers': ['console', ],
            'level': 'INFO',
            'propagate': True,
        }
    }
}

from apps.vote.settings import *
from apps.wh.settings import *
from search_settings import *
from apps.karma.settings import *

import djcelery
djcelery.setup_loader()
