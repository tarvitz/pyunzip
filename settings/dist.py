# coding: utf-8
# Django settings for WarMist project.
import os, sys
from settings_path import rel_path
try:
    import psycopg2
except ImportError:
    from psycopg2ct import compat
    compat.register()
#from apps import djcelery
#djcelery.setup_loader()
DEBUG=False

ADMINS = (
    ('Saul Tarvitz', 'tarvitz@blacklibrary.ru'),
)

DATABASES={
    'default':{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db'
    }
}

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
LOCALE_PATHS = (
    rel_path('conf/locale'),
)
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True


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
STYLES_URL = '/styles/'

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
    #'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'apps.core.middleware.ChecksMiddleware',
    'apps.core.middleware.UserActivityMiddleware',
    'apps.core.middleware.GuestActivityMiddleware',
    'apps.core.middleware.TestMiddleware',
    #obsolete
    #'apps.core.middleware.UserSettingsMiddleware',
    'apps.wh.middleware.WarningsMiddleware',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211',
        ]
    }
}

ROOT_URLCONF = 'urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    #deprecated
    #'django.core.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
    'apps.core.context_processors.global_settings',
    #'apps.core.context_processors.expressions',
    #'apps.core.context_processors.briefing_news',
    #'apps.core.context_processors.last_replays',
    #'apps.core.context_processors.pm',
    #'apps.core.context_processors.user_settings',
    'apps.core.context_processors.core',
    #'apps.core.context_processors.global_referer',
    #'apps.core.context_processors.base_template',
    #'apps.core.context_processors.session',
    'apps.menu.context_processors.menu',
)
TEMPLATE_DIRS = (
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
    'filters': {
         'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false', ],
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
    #'django.contrib.flatpages',
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
    #'apps.blogs',
    'apps.tracker',
    'apps.farseer',
    'apps.pybb',
    'apps.menu',
    'djcelery',
    'apps.djangosphinx',
    'extwidgets',
    'south',
    'sorl.thumbnail',
    #
    'grappelli',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
)
#settings
DOMAIN='w40k.net'
ALLOWED_HOSTS = ('w40k.net', 'www.w40k.net', )
APP_VOTE_ENABLED=True
PRODUCTION=get_local('PRODUCTION', True)
DEVELOPMENT=get_local('DEVELOPMENT', False)
YANDEX_METRICA_ENABLED = get_local('YANDEX_METRICA_ENABLED', False)
BOOTSTRAP_VERSION='3'
ENABLE_500_TEST=False
SERVER_EMAIL='noreply@w40k.net'
DEV_SERVER=True
GRAPPELLI_ADMIN_TITLE='w40k.net'
USE_OLD_THUMBNAIL_IMAGE_SCHEME=False
DEFAULT_TEMPLATE='base.html'
DEFAULT_SYNTAX='textile'
IMAGE_THUMBNAIL_SIZE='200x200'
BRUTEFORCE_ITER=10
SEND_MESSAGES=True
OBJECTS_ON_PAGE=20
EXPEREMENTAL=False
USER_FILES_LIMIT=100*1024*1024
# TEMPLATES INCLUES
DOCUMENT = {
    'links': 'links.html',
    'pages': 'pages.html',
    'comments': 'comments.html',
    'comments_form': 'add_comment.html',
    'replay_inc': 'replays/includes/replay.html',
    'replays_inc': 'replays/includes/replays.html',
    'search_inc': 'includes/search.html',
    'news_inc': 'includes/news.html',
    'rosters_inc': 'includes/rosters.html',
    'roster_inc': 'includes/roster.html',
    'battle_report_inc': 'includes/battle_report.html',  # obsolete
    'nothing_inc': 'nothing.html',
    'article_inc': 'includes/article.html',
    'image_inc': 'gallery/includes/image.html',
    'sph_search_inc': 'includes/sphinx_search.html'
}

from apps.vote.settings import *
from apps.wh.settings import *
from search_settings import *
from apps.karma.settings import *

#import djcelery
#djcelery.setup_loader()
# Celery settings
# Time after task will be expired, 5 hours
#CELERY_TASK_RESULT_EXPIRES = 18000
# Send notifications for admins if troubles would happen
#CELERND_TASK_ERROR_EMAILS = True
#CELERY_RESULT_BACKEND = "redis"
#CELERY_REDIS_HOST = "redis"
#CELERY_REDIS_PORT = 6379
#CELERY_REDIS_DB = 0
#BROKER_URL = "redis://redis:6379/0"

DEBUG_TOOLBAR=False
DEBUG=True
if DEBUG and DEBUG_TOOLBAR:
    INTERNAL_IPS = ('127.0.0.1',)
    INSTALLED_APPS += (
        'debug_toolbar',
        'debug_toolbar_extra',
    )
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
    DEBUG_TOOLBAR_PANELS = (
        'debug_toolbar.panels.version.VersionDebugPanel',
        'debug_toolbar.panels.timer.TimerDebugPanel',
        'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
        'debug_toolbar.panels.headers.HeaderDebugPanel',
        'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
        'debug_toolbar.panels.template.TemplateDebugPanel',
        'debug_toolbar.panels.sql.SQLDebugPanel',
        'debug_toolbar.panels.signals.SignalDebugPanel',
        'debug_toolbar.panels.logger.LoggingPanel',
        'debug_toolbar_extra.panels.PrintTemplateNamePanel',
    )
