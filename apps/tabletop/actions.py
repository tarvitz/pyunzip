# coding: utf8
from django.utils.translation import ugettext_lazy as _, ugettext as _tr
from django.http import HttpResponse, HttpResponseRedirect, Http404
from apps.core.shortcuts import direct_to_template

def alter_codex_action(request, qset, model, **kwargs):
    from apps.tabletop.forms import ActionAlterRosterCodex
    template = 'tabletop/actions/alter_roster_codex.html'
    if request.method == 'POST':
        form = ActionAlterRosterCodex(request.POST, model=model, qset=qset)
        if form.is_valid():
            for q in qset:
                q.codex = form.cleaned_data['codex']
                q.revision = form.cleaned_data.get('revision', None) or q.revision
                q.save()
            return {'qset': qset}
        else: 
            return {'response': direct_to_template(request, template,
                {'form': form})}
    return {'qset': qset }
alter_codex_action.short_description = _('alter codex')
