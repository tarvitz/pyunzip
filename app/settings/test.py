# coding: utf-8

from .dist import *
from .messages import *
try:
    from .local import *
except ImportError:
    pass


DEBUG = TEMPLATE_DEBUG = True

DEV_SERVER = True
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': [
            '127.0.0.1:11211',
        ],
        'KEY_PREFIX': 'tests'
    }
}
INSTALLED_APPS += ('tests', )
INSTALLED_APPS = list(INSTALLED_APPS)
USER_FILES_LIMIT = 1.2 * 1024 * 1024
SEND_MESSAGES = True

KARMA_PER_TIMEOUT_AMOUNT = 100

MEDIA_ROOT = rel('db/tests/uploads')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': rel_path('db/_wh.sqlite'),
    }, 
}

removable = ['south', ]
for app in removable:
    if app in INSTALLED_APPS:
        INSTALLED_APPS.remove(app)

TEST_DATABASE_NAME = DATABASES['default']['NAME'] if \
    DATABASES['default']['NAME'].startswith('test_') else \
    'test_' + DATABASES['default']['NAME']

if 'django_plop.middleware.PlopMiddleware' in MIDDLEWARE_CLASSES:
    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)
    MIDDLEWARE_CLASSES.pop(MIDDLEWARE_CLASSES.index(
        'django_plop.middleware.PlopMiddleware'))

# internal apps
MIGRATION_MODULES = {
    app: "apps.%s.migrations_not_used_in_tests" % app
    for app in ["accounts", "tabletop", "wh", "core",
                "files", "karma", "menu", "news", "pybb",
                "comments",]
}
# django apps
MIGRATION_MODULES.update({
    app: "django.contrib.%s.migrations_not_used_in_tests" % app
    for app in ["sites", "admin", "auth", "contenttypes", "sessions"]
})

# third-party apps
MIGRATION_MODULES.update({
    app: "%s.migrations_not_used_in_tests" % app
    for app in ['django_cron', ]
})

REDIS.update({
    'db': 13
})