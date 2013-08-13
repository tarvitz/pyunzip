from dist import *
from messages import *
from local import *
from initials import *

SECRET_KEY='df!2313asd12345fkasdi#)!@#j131203(421dasjf'
DATABASES={
    'default':{
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'wh_production',
        'USER': 'wh',  # Not used with sqlite3.
        'PASSWORD': 'wh',  # Not used with sqlite3.
        'HOST': 'localhost',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',  # Set to empty string for default. Not used with sqlite3.

    }
}
BOOTSTRAP_VERSION='3'
DEBUG_TOOLBAR=False
DEBUG=True

INTERNAL_IPS = ('127.0.0.1',)
if DEBUG_TOOLBAR and DEBUG:
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
