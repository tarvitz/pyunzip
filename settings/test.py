# coding: utf-8
from settings.dist import *
from settings.local import *
from settings.dist import INSTALLED_APPS

INSTALLED_APPS += ('tests',)
INSTALLED_APPS = list(INSTALLED_APPS)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '_wh.sqlite',
    }, 
}

removable = ['south', ]
for app in removable:
    if app in INSTALLED_APPS:
        INSTALLED_APPS.remove(app)

TEST_DATABASE_NAME = DATABASES['default']['NAME'] if \
    DATABASES['default']['NAME'].startswith('test_') else \
    'test_' + DATABASES['default']['NAME']

#
def _to_uni(value):
    try:
        return str(value)
    except:
        try:
            return str(value.message.encode('utf-8'))
        except:
            return '<unprintable %s object>' % type(value).__name__
import traceback
traceback._some_str = _to_uni
