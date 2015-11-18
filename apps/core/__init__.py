# coding: utf-8
from django.utils.translation import ugettext_lazy as _

default_app_config = 'apps.core.apps.CoreConfig'
module_name = _('core')


def get_skin_template(user, template):
    return template
