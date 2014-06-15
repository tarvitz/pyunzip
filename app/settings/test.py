# coding: utf-8
#from .dist import *
#from .local import *
#from .messages import *
#from .initials import *
from app.settings.dist import *
from app.settings.local import *
from app.settings.messages import *
from app.settings.initials import *

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
