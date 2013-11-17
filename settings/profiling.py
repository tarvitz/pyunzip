from .dist import *
try:
    from .local import *
except ImportError:
    pass

MIDDLEWARE_CLASSES += ('django_plop.middleware.PlopMiddleware', )
PLOP_DIR = rel_path('data/plop')

from .messages import *
from .initials import *
