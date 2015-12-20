# coding: utf-8
from django.utils.translation import ugettext_lazy as _

default_app_config = 'apps.core.apps.CoreConfig'
module_name = _('core')

__title__ = 'Core module'
__version__ = '1.0'
__author__ = 'Nickolas Fox'
__license__ = 'BSD'
__copyright__ = 'Copyright 2008-2015 Nickolas Fox'

# Version synonym
VERSION = __version__


def get_skin_template(user, template):
    return template
