# coding: utf-8
# Django settings for WarMist project.
import os
from settings_path import rel_path
try:
    import psycopg2
except ImportError:
    try:
        from psycopg2ct import compat
        compat.register()
    except ImportError:
        pass

DEBUG = False
ADMINS = (
    ('Saul Tarvitz', 'tarvitz@blacklibrary.ru'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite.db'
    }
}

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

_ = lambda s: s

# TODO: cleanup
STYLES_ROOT = rel_path('styles')
ADMIN_MEDIA = rel_path('admin_media')
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/uploads/'
STATIC_URL = '/media/'
STYLES_URL = '/styles/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

STATIC_ROOT = ''
MEDIA_ROOT = rel_path('uploads')

STATICFILES_DIRS = (
    rel_path('media'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'apps.core.middleware.BanMiddleware',
    'apps.core.middleware.ChecksMiddleware',
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
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
    'apps.core.context_processors.global_settings',
    'apps.core.context_processors.core',
    'apps.menu.context_processors.menu',
    'apps.news.context_processors.weekly_events',
)

TEMPLATE_DIRS = (
    rel_path('templates'),
)

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
    'apps.accounts',
    'apps.core',
    'apps.comments',
    'apps.jsonapp',
    #
    'apps.wh',
    'apps.news',
    'apps.files',
    'apps.tabletop',
    'apps.vote',
    'apps.tagging',
    'utils',
    'apps.karma',
    'apps.tracker',
    'apps.farseer',
    'apps.pybb',
    'apps.menu',
    'extwidgets',
    'django_extensions',
    'south',
    'rest_framework',
    'captcha',
    'sorl.thumbnail',
    'grappelli',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'gunicorn',
    'django_cron',
    'django_select2',
)

SOUTH_MIGRATION_MODULES = {
    'comments': 'apps.comments.migrations',
}

AUTH_USER_MODEL = (
    'accounts.User' if 'apps.accounts' in INSTALLED_APPS else 'auth.User'
)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    #'apps.accounts.backends.EmailAuthBackend',
)

CRON_CLASSES = (
    'apps.pybb.cron.UpdatePollJob',
    'apps.news.cron.EventsMarkFinishedCronJob'
)


REST_FRAMEWORK = {
    #'DEFAULT_PERMISSION_CLASSES': (
    #    'rest_framework.permissions.IsAdminUser',),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',),
    'PAGINATE_BY': 50
}

#settings
DOMAIN = 'w40k.net'
ALLOWED_HOSTS = ('w40k.net', 'www.w40k.net', 'me.w40k.net', 'localhost')
APP_VOTE_ENABLED = True
PRODUCTION = True
DEVELOPMENT = False
YANDEX_METRICA_ENABLED = False
BOOTSTRAP_VERSION = ''
ENABLE_500_TEST = False
SERVER_EMAIL = 'noreply@w40k.net'
DEV_SERVER = True
GRAPPELLI_ADMIN_TITLE = 'w40k.net'
USE_OLD_THUMBNAIL_IMAGE_SCHEME = False
DEFAULT_TEMPLATE = 'base.html'
DEFAULT_SYNTAX = 'textile'
IMAGE_THUMBNAIL_SIZE = '200x200'
BRUTEFORCE_ITER = 10
SEND_MESSAGES = True
OBJECTS_ON_PAGE = 20
EXPEREMENTAL = False
USER_FILES_LIMIT = 100*1024*1024
MAXIMUM_POLL_ITEMS_AMOUNT = 10
NULL_AVATAR_URL = os.path.join(MEDIA_URL, 'avatars/none.png')

FORUM_THEME_DEFAULT = 'primary'
FORUM_THEMES = (
    # <name>, panel-<class>
    (_('winter'), 'primary'),
    (_('summer'), 'warning'),
    (_('autumn'), 'danger'),
    (_("spring"), 'success'),
    (_("void"), 'default')
)
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

MAXIMUM_WORDS_COUNT_BEFORE_HIDE = 500
MAX_DOCUMENT_SIZE = 1024 * 4  # 4096 bytes

DEBUG_TOOLBAR = False
DEBUG = True
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
