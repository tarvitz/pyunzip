# coding: utf-8
#from settings_path import *
#from settings_net import *
from .dist import *
try:
    from .local import *
except ImportError:
    pass
from .messages import *
from .initials import *
#from settings_quotes import *
