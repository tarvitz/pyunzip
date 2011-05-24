# coding: utf-8
# model actions
from django.utils.translation import ugettext_lazy as _, ugettext as _tr
def file_delete_qset(request, qset):
    (q.file.delete(save=False) for q in qset)
    return qset.delete()
file_delete_qset.short_description = _('delete')

