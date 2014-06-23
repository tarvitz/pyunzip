from .dist import INSTALLED_APPS, MIDDLEWARE_CLASSES

SECRET_KEY='df!2313asd12345fkasdi#)!@#j131203)421dazjf'
"""
DATABASES={
    'default':{
        'ENGINE': 'django.db.backends.postgresql_psycopg2',  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'wh',
        'USER': 'wh',  # Not used with sqlite3.
        'PASSWORD': 'wh',  # Not used with sqlite3.
        'HOST': 'localhost',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5432',  # Set to empty string for default. Not used with sqlite3.

    }
}
"""
BOOTSTRAP_VERSION='3'
DEV_SERVER = DEVELOPMENT = True
DEBUG = TEMPLATE_DEBUG = True
OBJECTS_ON_PAGE = 20
RECAPTCHA_PUBLIC_KEY = '' # Recaptcha public key
RECAPTCHA_PRIVATE_KEY = ''
RECAPTCHA_USE_SSL = True
EMAIL_HOST='smtp.gmail.com'
EMAIL_HOST_USER='user@gmail.com'
EMAIL_HOST_PASSWORD='password'
EMAIL_FEEDBACK_HOST_PASSWORD='password'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

DEBUG_TOOLBAR = False

if DEBUG_TOOLBAR:
    INTERNAL_IPS = ('127.0.0.1', 'localhost', )
    INSTALLED_APPS += (
        'debug_toolbar',
        'debug_toolbar_extra',
    )
    MIDDLEWARE_CLASSES += (
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    )
