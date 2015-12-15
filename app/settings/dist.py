# coding: utf-8
# Django settings for WarMist project.
import os
from .settings_path import rel_path

DEBUG = False
ADMINS = (
    ('Saul Tarvitz', 'tarvitz@blacklibrary.ru'),
)

SECRET_KEY = 'some secret key is here'

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
STATIC_ROOT = rel_path('static_root')

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin_media/'

MEDIA_ROOT = rel_path('db/uploads')

STATICFILES_DIRS = (
    'static',
    rel('static')
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            rel('templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.global_settings',
                'apps.core.context_processors.core',
                'apps.menu.context_processors.menu',
                'apps.news.context_processors.weekly_events',
                'apps.news.context_processors.notes',
                'apps.comments.context_processors.comment_watches',
            ],
        },
    },
]

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
        }
    },

}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.sitemaps',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',

    'apps.accounts',
    'apps.core',
    'apps.comments',

    'apps.wh',
    'apps.news',
    'apps.files',
    'apps.tabletop',
    'apps.karma',
    'apps.pybb',
    'apps.menu',
    'rest_framework',
    'captcha',
    'sorl.thumbnail',
    'haystack',
    # 'django_cron',
)


AUTH_USER_MODEL = 'accounts.User'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'apps.accounts.backends.EmailAuthBackend',
)

FIXTURE_DIRS = (
    rel('tests/fixtures'),
)

CRON_CLASSES = (
    'apps.pybb.cron.UpdatePollJob',
    'apps.news.cron.EventsMarkFinishedCronJob',
    'apps.accounts.cron.PolicyWarningsMarkExpireCronJob',
)

API_OBJECTS_ON_PAGE = 50

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',),
    'DEFAULT_PAGINATION_CLASS': (
        'rest_framework.pagination.LimitOffsetPagination'
    ),
    'PAGE_SIZE': API_OBJECTS_ON_PAGE
}


#settings
DOMAIN = 'w40k.net'
ALLOWED_HOSTS = ('w40k.net', 'www.w40k.net', 'me.w40k.net', 'localhost')

PRODUCTION = True
DEV_SERVER = True

DEFAULT_TEMPLATE = 'pybb/base.html'
DEFAULT_SYNTAX = 'textile'
IMAGE_THUMBNAIL_SIZE = '200x200'
BRUTEFORCE_ITER = 10
SEND_MESSAGES = True
OBJECTS_ON_PAGE = 20
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

#: haystack
#: HAYSTACK
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': (
            'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine'
        ),
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'warmist',
    },
}
