# coding: utf8
from django.utils.translation import ugettext_lazy as _, ugettext as _tr

def common_delete_action(request, qset):
    return qset.delete()
common_delete_action.short_description = _('delete')
