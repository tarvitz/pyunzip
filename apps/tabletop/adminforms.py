# coding: utf-8
import re

from django import forms
from django.db.utils import IntegrityError
from django.db.models import Manager
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.forms.models import modelformset_factory, BaseInlineFormSet
from django.utils.safestring import mark_safe
from apps.tabletop.models import Wargear, ModelUnit, AutoRoster, MWRUnit
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
            if not model_unit in link.model_units.all():
                titles = ", ".join([i.title for i in link.model_units.all()])
                msg = _("You can not link '%(src)s %(link)s' with '%(target)s' unit") % {
                    'src': titles,
                    'link': link.title,
                    'target': model_unit.title
                }
                self._errors['link'] = ErrorList([msg])
        if amount > limit:
            msg = _("You can not set amount more than its "
                "wargear limit with '%s'"
            ) % limit
            self._errors['amount'] = ErrorList([msg])

        # checking threshold limits
        gear_amount = int(self.data[self.prefix + '-amount'])
        unit_amount = int(self.data['amount'] or 0)
        if (unit_amount / link.threshold) < gear_amount:
            msg = _("You can not take '%(gear_amount)s' number(s) of wargear, "
            "because it depends on unit models amount, one point of wargear "
            "each '%(threshold)s' models in unit") % {
                'gear_amount': gear_amount,
                'threshold': link.threshold
            }
            if 'amount' in self._errors:
                self._errors['amount'] += ErrorList([msg])
            else:
                self._errors['amount'] = ErrorList([msg])

        #
        #   checking dependencies
        #
        return cd

class UnitWargearContainerFormset(BaseInlineFormSet):
    def clean(self):
        links_pk = [i.data.get(i.prefix + '-link', '0') for i in self.forms]
        links_amount = [int(i.data.get(i.prefix + '-amount', 0)) for i in self.forms]

        links = Wargear.objects.filter(pk__in=links_pk)
        model_unit_pk = self.data.get('model_unit', 0)
        roster_pk = self.data.get('roster', 0)
        model_unit = get_object_or_None(ModelUnit, pk=model_unit_pk)
        roster = get_object_or_None(AutoRoster, pk=roster_pk)

        mwr_amount = model_unit.mwr_amount or 0
        requirements = model_unit.requirements
        limit = 0
        for form in self.forms:
            # limit accomulator
            if form.instance.link.pk in [i['wargear__pk'] for i in requirements.values('wargear__pk')]:
                limit += form.instance.amount

        # checking outside formset
        """
        if requirements:
            require_list = ", ".join([i.wargear.title for i in requirements.all()])
            matches = requirements.filter(wargear__in=links)

            if limit != mwr_amount:
                msg = mark_safe(_("You should append '%(amount)s' "
                    "required upgrades, not less neither more, please "
                    "select them from the following list: \n<br>%(list)s") % {
                    'amount': mwr_amount,
                    'list': require_list
                })
                if len(self._errors) > 0:
                    errors = [msg, self._errors[0].get('link') or '']
                    self._errors[0]['link'] = ErrorList(errors)
        """

        # check blockages within wargear adding
        for (form_index, form) in enumerate(self.forms):
            link_pk = form.data[form.prefix + '-link']
            link = get_object_or_None(Wargear, pk=link_pk)

            dependency_manager = safe_get([link, 'wargear_requirements'])
            if all((isinstance(dependency_manager, Manager), model_unit)):
                # check wargear requirements
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

            # check unit wargear requirements
            dependency_manager = safe_get([link, 'unit_wargear_requirements'])
            if all((isinstance(dependency_manager, Manager), model_unit)):
                depend = [i['require__pk'] for i in dependency_manager.values('require__pk')]
                units = ModelUnit.objects.filter(pk__in=depend)
                dependencies = ", ".join(
                    [i.title for i in ModelUnit.objects.filter(pk__in=depend)]
                )
                satisfy_count = roster.unit_containers.filter(model_unit__in=units).count()
                real_count = units.count()
                if depend and satisfy_count < real_count:
                    msg = _("You can not add this wargear or "
                        "upgrade before add '%s' to your army list (roster)") % dependencies
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

            # end for form in self.forms

        #
        #   checking combined wargear and its limits
        #
        model_unit_amount = int(self.data.get('amount', 0))
        if all((links, model_unit)):
            for (link_amount, link_pk, form_index) in zip(links_amount, links_pk, xrange(len(self.forms))):

                link = get_object_or_None(Wargear, pk=link_pk)
                combines = [i['pk'] for i in link.combines.values('pk')]
                if not combines:
                    # skip not combined wargears
                    continue

                additional_amount = 0
                for pk in combines:
                    additional_amount += links_amount[links_pk.index(str(pk))]
                amount = link_amount + additional_amount
                if amount > (model_unit_amount / link.threshold):
                    _limit = model_unit_amount / link.threshold
                    msg = _("Combines weapon reach its limits, please add weapons "
                    "below '%s' limit") % _limit
                    if 'amount' in self._errors[form_index]:
                        self._errors[form_index]['amount'] += ErrorList([msg])
                    else:
                        self._errors[form_index]['amount'] = ErrorList([msg])
        super(UnitWargearContainerFormset, self).clean()


class InlineMWRUnitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InlineMWRUnitForm, self).__init__(*args, **kwargs)
        model_unit = get_object_or_None(ModelUnit, pk=self.initial.get('model_unit'))
        try:
            if model_unit:
                self.fields['wargear'].queryset = Wargear.objects.filter(
                    model_units__in=[model_unit]
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

    def clean(self):
        cd = self.cleaned_data
        # checking MRW outside formset clean method
        amount = cd.get('amount', 0)
        is_formset = 'wargear_containers-MAX_NUM_FORMS' in self.data
        rprefix = re.compile(r'(wargear_containers-\d+)-unit')
        _prefixes = rprefix.findall(" ".join(self.data.keys()))
        prefixes = []

        # forms marks to deletion count as deleted so some checks
        # for ModelWargearRequirement Units should be proceeded
        for p in _prefixes:
            if self.data.get(p+'-DELETE') != 'on':
                prefixes.append(p)

        links_pk = [self.data.get(prefix + '-link', '0') for prefix in prefixes]
        links_amount = [int(self.data.get(prefix + '-amount', 0)) for prefix in prefixes]
        links = Wargear.objects.filter(pk__in=links_pk)

        model_unit = cd.get('model_unit', None)
        if all((amount, is_formset, model_unit)):
            satisfy_count = model_unit.requirements.count()
            real_count = model_unit.requirements.filter(wargear=links).count()

            if satisfy_count != real_count:
                dependencies = ", ".join([i.wargear.title for i in model_unit.requirements.all()])
                msg = _("This unit requires wargear includes: '%s' "
                "to proceed, please add them") % dependencies
                self._errors['model_unit'] = ErrorList([msg])
            else:
                # checking thresholds
                for (link_amount, link, idx) in zip(links_amount, links, xrange(len(prefixes))):
                    requirement = get_object_or_None(MWRUnit, wargear=link, model_unit=model_unit)
                    if not requirement.threshold:
                        continue # skip non thresholded mwrs
                    if (amount / requirement.threshold) > link_amount:
                        msg = _("Every '%(threshold)s' models you should append 1 additional"
                        "to your %(wargear)s link") % {
                            'threshold': requirement.threshold,
                            'wargear': requirement.wargear.title
                        }
                        errors = [msg, self._errors['model_unit'] if 'model_unit' in self._errors else '']
                        self._errors['model_unit'] = ErrorList(errors)
        return cd
