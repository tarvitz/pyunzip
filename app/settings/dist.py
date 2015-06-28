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
        'NAME': rel_path('db/sqlite.db'),
    }
}

def rel(path):
    return os.path.join(
        os.path.join(os.path.dirname(__file__), '../..'), path)

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

ADMIN_MEDIA = rel_path('admin_media')
# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/uploads/'
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

STATIC_ROOT = ''
MEDIA_ROOT = rel_path('db/uploads')

STATICFILES_DIRS = (
    'static',
    rel('static')
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
    'apps.accounts.middleware.ReadOnlyMiddleware',
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211',
        ]
    }
}

ROOT_URLCONF = 'app.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.static',
    'apps.core.context_processors.global_settings',
    'apps.core.context_processors.core',
    'apps.menu.context_processors.menu',
    'apps.news.context_processors.weekly_events',
    'apps.news.context_processors.notes',
    'apps.comments.context_processors.comment_watches',
)

TEMPLATE_DIRS = (
    rel_path('templates'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '%(levelname)s %(asctime)s %(module)s '
                '%(process)d %(thread)d %(message)s')
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
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        'apps.accounts': {
            'level': "INFO",
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.comments': {
            'level': "INFO",
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.karma': {
            'level': "INFO",
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.news': {
            'level': "INFO",
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.pybb': {
            'level': "INFO",
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.tabletop': {
            'level': "INFO",
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.wh':{
            'level': "INFO",
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.files': {
            'level': "INFO",
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.core': {
            'level': 'INFO',
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.thirdpaty.sleekxmpp.basexmpp': {
            'level': 'INFO',
            'propagate': True,
            'handlers': ['console', ],
        },
        'apps.thirdpaty.sleekxmpp.xmlstream.xmlstream': {
            'level': 'INFO',
            'propagate': True,
            'handlers': ['console', ],
        },
    },

}

INSTALLED_APPS = (
    'django.contrib.sitemaps',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'apps.accounts',
    'apps.core',
    'apps.comments',
    'apps.jsonapp',
    #
    'apps.wh',
    'apps.news',
    'apps.files',
    'apps.tabletop',
    'apps.utils',
    'apps.karma',
    'apps.pybb',
    'apps.menu',
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
)

SOUTH_MIGRATION_MODULES = {
    'comments': 'apps.comments.migrations',
}

AUTH_USER_MODEL = (
    'accounts.User' if 'apps.accounts' in INSTALLED_APPS else 'auth.User'
)
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'apps.accounts.backends.EmailAuthBackend',
)

CRON_CLASSES = (
    'apps.pybb.cron.UpdatePollJob',
    'apps.news.cron.EventsMarkFinishedCronJob',
    'apps.accounts.cron.PolicyWarningsMarkExpireCronJob',
)

API_OBJECTS_ON_PAGE = 50

REST_FRAMEWORK = {
    #'DEFAULT_PERMISSION_CLASSES': (
    #    'rest_framework.permissions.IsAdminUser',),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',),
    'PAGINATE_BY': API_OBJECTS_ON_PAGE,
    'PAGINATE_BY_PARAM': 'page_size',
}


#settings
DOMAIN = 'w40k.net'
ALLOWED_HOSTS = ('w40k.net', 'www.w40k.net', 'me.w40k.net', 'localhost')

PRODUCTION = True
DEVELOPMENT = False
YANDEX_METRICA_ENABLED = False

SERVER_EMAIL = 'noreply@w40k.net'
DEV_SERVER = True
GRAPPELLI_ADMIN_TITLE = 'w40k.net'

DEFAULT_TEMPLATE = 'base_template.html'
DEFAULT_SYNTAX = 'textile'
IMAGE_THUMBNAIL_SIZE = '200x200'
BRUTEFORCE_ITER = 10
SEND_MESSAGES = True
OBJECTS_ON_PAGE = 20
EXPEREMENTAL = False
USER_FILES_LIMIT = 100 * 1024 * 1024
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
CSS_THEMES = (
    (_('light theme'), 'light'),
    (_('dark theme'), 'dark')
)

# TEMPLATES INCLUDES, todo: cleanup
DOCUMENT = {
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

SYNTAX = (
    ('textile', 'textile'), ('bb-code', 'bb-code'),
)

SIGN_CHOICES = (
    (1, '[*]'),
    (2, '[*][*]'),
    (3, '[+]'),
    (4, '[+][+]'),
    (5, '[x]'),
    (6, '[x][x]'),
    (7, _('[ban]')),
    (8, _('[everban]')),
)


READONLY_LEVEL = 40000
GLOBAL_SITE_NAME = 'http://w40k.net'

KARMA_PER_TIMEOUT_AMOUNT = 1
KARMA_COMMENTS_COUNT = 1
KARMA_TIMEOUT_MINUTES = 60 * 24  # whole day
MAXIMUM_WORDS_COUNT_BEFORE_HIDE = 500
MAX_DOCUMENT_SIZE = 1024 * 4
FROM_EMAIL = 'AstroPath (no replay) <astropath@blacklibrary.ru>'

#: captcha settings
NOCAPTCHA = True
