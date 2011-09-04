import sys
import os

#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/..')
PROJECT_ROOT = os.path.dirname(__file__)
if not PROJECT_ROOT in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.environ['CELERY_LOADER'] = 'django'
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
