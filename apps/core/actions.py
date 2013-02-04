# coding: utf-8
from django.utils.translation import ugettext_lazy as _, ugettext as _tr
from apps.core.forms import ActionApproveForm
from django.http import HttpResponse, HttpResponseRedirect, Http404
from apps.core.shortcuts import direct_to_template

def common_delete_action(request, qset, model, **kwargs):
    template = 'core/action_delete_form.html'
    if request.method == 'POST':
        form = ActionApproveForm(request.POST, model=model, qset=qset)
        if form.is_valid():
            return {'qset': qset.delete()}
        else: 
            return {'response': direct_to_template(request, template,
                {'form': form})}
    return {'qset': qset }
common_delete_action.short_description = _('delete')
