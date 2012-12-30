# coding: utf-8
from django import forms
from django.db.utils import IntegrityError
from django.db.models import Manager
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelformset_factory, BaseInlineFormSet
from django.utils.safestring import mark_safe
from apps.tabletop.models import Wargear
from functools import partial

get = lambda x, y: getattr(x, y) if hasattr(x, y) else None
safe_get = partial(reduce, get)

class AddWargearContainerForm(forms.ModelForm):
    #def __init__(self, *args, **kwargs):
    #    super(AddWargearContainerForm, self).__init__(*args, **kwargs)

    def clean(self):
        """ checks for clean add """
        cd = self.cleaned_data

        #
        #    checking amount
        #

        #limit = safe_get([instance, 'link', 'limit'])
        amount = cd.get('amount') or None
        link = cd.get('link') or None
        unit = cd.get('unit') or None
        limit = safe_get([link, 'limit'])

        #
        #   validating unit and link (wargear)
        #
        if all((link, unit)):
            if link.model_unit != unit.model_unit:
                msg = _("You can not link '%(src)s %(link)s' with '%(target)s' unit") % {
                    'src': link.model_unit.title,
                    'link': link.title,
                    'target': unit.model_unit.title
                }
                self._errors['link'] = ErrorList([msg])
        if amount > limit:
            msg = _("You can not set amount more than its "
                "wargear limit with '%s'"
            ) % limit
            self._errors['amount'] = ErrorList([msg])

        #
        #   checking dependencies
        #

        dependency_manager = safe_get([link, 'wargear_requirements'])

        if all((isinstance(dependency_manager, Manager), unit)):
            depend = [i['require__pk'] for i in dependency_manager.values('require__pk')]
            dcontainers = unit.wargear_containers.filter(link__in=depend)
            dependencies = ", ".join(
                [i.title for i in Wargear.objects.filter(pk__in=depend)]
            )

            if depend and not dcontainers:
                msg = _("You can not add this wargear or "
                    "upgrade before your add '%s' to given unit") % dependencies
                self._errors['link'] = ErrorList([msg])

        #
        #   checking blockages
        #
        if all((link.blocks.all(), unit)):
            src = ''
            links = link.blocks.all()
            if self.instance:
                links = links.exclude(pk=self.instance.link.pk if hasattr(self.instance, 'link') else 0)
            nblocks = unit.wargear_containers.filter(link__in=links)
            if nblocks:
                dst = link.title
                src = ", ".join([i.title for i in link.blocks.all()])
                msg = _("You can not add any of these titles: "
                    "'%(dst)s' before delete '%(src)s'") % {
                    'dst': dst,
                    'src': src
                }
                self._errors['link'] = ErrorList([msg])
        return cd

class WargearContainerForm(AddWargearContainerForm):
    def clean(self):
        cd = super(WargearContainerForm, self).clean()
        return cd

class UnitWargearContainerFormset(BaseInlineFormSet):
    def clean(self):
        links = [i.instance.link for i in self.forms]
        require = self.instance.model_unit.mwr_amount or 0
        requirements = self.instance.model_unit.requirements
        limit = 0
        for form in self.forms:
            if form.instance.link.pk in [i['wargear__pk'] for i in requirements.values('wargear__pk')]:
                limit += form.instance.amount
        require_list = ", ".join([i.wargear.title for i in requirements.all()])
        matches = requirements.filter(wargear__in=links)

        if limit != require:
            msg = mark_safe(_("You should append '%(amount)s' "
                "required upgrades, not less neither more, please "
                "select them from the following list: \n<br>%(list)s") % {
                'amount': require,
                'list': require_list
            })
            errors = [msg, self._errors[0].get('link') or '']
            self._errors[0]['link'] = ErrorList(errors)
        super(UnitWargearContainerFormset, self).clean()
