# coding: utf-8
from django import forms
from django.db.utils import IntegrityError
from django.db.models import Manager
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelformset_factory, BaseInlineFormSet
from django.utils.safestring import mark_safe
from apps.tabletop.models import Wargear, ModelUnit
from apps.core.helpers import get_object_or_None
from django.core.exceptions import ObjectDoesNotExist
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
        model_unit = get_object_or_None(ModelUnit, pk=self.data.get('model_unit') or 0)
        try:
            unit = cd.get('unit') or None
            model_unit = unit.model_unit
        except ObjectDoesNotExist:
            pass
        limit = safe_get([link, 'limit'])

        #
        #   validating unit and link (wargear)
        #
        if all((link, unit)):
            if link.model_unit != model_unit:
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

class WargearContainerForm(forms.ModelForm):
    def clean(self):
        #cd = super(WargearContainerForm, self).clean()
        """ checks for clean add, duplicates WargearContainerForm clean method,
        but should be overrided to provide inlines add support for blockage
        and dependencies checks
        """
        cd = self.cleaned_data

        #
        #    checking amount
        #

        #limit = safe_get([instance, 'link', 'limit'])
        amount = cd.get('amount') or None
        link = cd.get('link') or None
        model_unit = get_object_or_None(ModelUnit, pk=self.data.get('model_unit') or 0)
        try:
            unit = cd.get('unit') or None
            model_unit = unit.model_unit
        except ObjectDoesNotExist:
            pass
        limit = safe_get([link, 'limit'])

        #
        #   validating unit and link (wargear)
        #
        if all((link, unit)):
            if link.model_unit != model_unit:
                msg = _("You can not link '%(src)s %(link)s' with '%(target)s' unit") % {
                    'src': link.model_unit.title,
                    'link': link.title,
                    'target': model_unit.title
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
        return cd

class UnitWargearContainerFormset(BaseInlineFormSet):
    def clean(self):
        links = [i.data.get(i.prefix + '-link', '0') for i in self.forms]
        links = Wargear.objects.filter(pk__in=links)
        model_unit_pk = self.data.get('model_unit', 0)
        model_unit = get_object_or_None(ModelUnit, pk=model_unit_pk)
        require = model_unit.mwr_amount or 0
        requirements = model_unit.requirements
        limit = 0
        for form in self.forms:
            if form.instance.link.pk in [i['wargear__pk'] for i in requirements.values('wargear__pk')]:
                limit += form.instance.amount

        if requirements:
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

        # check blockages within wargear adding
        for (form_index, form) in enumerate(self.forms):
            link_pk = form.data[form.prefix + '-link']
            link = get_object_or_None(Wargear, pk=link_pk)

            dependency_manager = safe_get([link, 'wargear_requirements'])
            if all((isinstance(dependency_manager, Manager), model_unit)):
                depend = [i['require__pk'] for i in dependency_manager.values('require__pk')]
                #dcontainers = unit.wargear_containers.filter(link__in=depend)
                dependencies = ", ".join(
                    [i.title for i in Wargear.objects.filter(pk__in=depend)]
                )
                satisfy_count = links.filter(pk__in=depend).count()
                real_count = link.wargear_requirements.count()
                if depend and satisfy_count < real_count:
                    msg = _("You can not add this wargear or "
                        "upgrade before your add '%s' to given unit") % dependencies
                    self._errors[form_index]['link'] = ErrorList([msg])

            #
            #   checking blockages
            #
            if all((link.blocks.all(), model_unit)):
                src = ''
                blocks = link.blocks.all()
                #if self.instance:
                #    links = links.exclude(pk=self.instance.link.pk if hasattr(self.instance, 'link') else 0)
                #nblocks = unit.wargear_containers.filter(link__in=blocks)
                if links.filter(pk__in=blocks):
                    dst = link.title
                    src = ", ".join([i.title for i in blocks.all()])
                    msg = _("You can not add any of these titles: "
                        "'%(dst)s' before delete '%(src)s'") % {
                        'dst': dst,
                        'src': src
                    }
                    self._errors[form_index]['link'] = ErrorList([msg])
        super(UnitWargearContainerFormset, self).clean()


class InlineMWRUnitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InlineMWRUnitForm, self).__init__(*args, **kwargs)
        model_unit = get_object_or_None(ModelUnit, pk=self.initial.get('model_unit', 0))
        try:
            if model_unit:
                self.fields['wargear'].queryset = Wargear.objects.filter(
                    model_unit = model_unit
                )
        except ObjectDoesNotExist:
            pass


class UnitContainerForm(forms.ModelForm):
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        model_unit_pk = self.data.get('model_unit', 0)
        model_unit = get_object_or_None(ModelUnit, pk=model_unit_pk)
        if amount:
            minimum = model_unit.min
            maximum = model_unit.max
            if amount < minimum or amount > maximum:
                raise forms.ValidationError(_("You can not add more models "
                    "than its limit allows, "
                    "min: '%(min)s', max: '%(max)s'") % {
                    'min': minimum,
                    'max': maximum
                })
        return amount
