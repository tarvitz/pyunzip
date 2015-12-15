# coding: utf-8
from django import forms
from django.utils.translation import (
    ugettext_lazy as _,
    pgettext_lazy
)

from apps.core.forms import RequestForm, RequestModelForm
from django.conf import settings
from apps.core.widgets import TinyMkWidget


from django.forms.utils import ErrorList
from apps.tabletop.models import Mission, Roster, Report, Codex

import re

from apps.wh.models import Side, Army

DEFAULT_ATTRS = {'class': 'form-control'}
SELECT2_ATTRS = {'class': 'form-control', 'data-toggle': 'select2'}


class AddCodexModelForm(forms.ModelForm):
    required_css_class = 'required'
    side = forms.ModelChoiceField(queryset=Side.objects)
    army = forms.ModelChoiceField(queryset=Army.objects.none(),
                                  required=False)

    class Meta:
        model = Codex
        fields = ['title', 'side', 'army', 'revisions', ]
        exclude = ['content_type', 'object_id', ]

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            instance = kwargs['instance']
            if instance:
                pass
        if args:
            POST = args[0]
            if 'army' in POST:
                if POST['army']:
                    self.base_fields['army'].queryset = Army.objects.filter(
                        pk=POST['army'])
        super(AddCodexModelForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(AddCodexModelForm, self).save(*args, **kwargs)


class AddBattleReportForm(RequestModelForm):
    title = forms.CharField(
        label=pgettext_lazy("Title", "battle report title"),
        help_text=_("battle report title, please be more creative"),
        widget=forms.TextInput(attrs={'class': 'span8 form-control'})
    )
    rosters = forms.ModelMultipleChoiceField(
        label=_("Rosters"),
        queryset=Roster.objects,
        help_text=_(
            "user rosters participating in the battle you want to describe"),
        widget=forms.SelectMultiple(
            attrs={'class': 'span8 form-control', 'data-class': 'ajax-chosen'}
        )
    )
    winners = forms.ModelMultipleChoiceField(
        label=_("Winners"),
        queryset=Roster.objects,
        help_text=_("winner or winners, should be at least one"),
        widget=forms.SelectMultiple(
            attrs={'class': 'span8 form-control', 'data-class': 'chosen'}
        )
    )

    mission = forms.ModelChoiceField(
        label=_("Mission"),
        queryset=Mission.objects,
        help_text=_('mission you played'),
        widget=forms.Select(
            attrs={'class': 'span8 form-control', 'data-class': 'chosen'}
        )
    )
    layout = forms.RegexField(
        regex=re.compile('^\d{1}vs\d{1}$'),
        label=_("Layout"),
        help_text=_(
            'how much players participated in the game, 1vs1, 2vs2 and so on'),
        widget=forms.TextInput(
            attrs={'class': 'span8 form-control'}
        )
    )

    comment = forms.CharField(
        label=pgettext_lazy("Content", "battle report content"),
        widget=forms.Textarea(
            attrs={'class': 'textile form-control'}
        )
    )
    next = forms.CharField(required=False, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AddBattleReportForm, self).__init__(*args, **kwargs)
        if not all((self.data or [None, ])) and not self.instance.pk:
            # data not posted
            none_rosters = Roster.objects.none()
            self.base_fields['rosters'].queryset = none_rosters
            self.fields['rosters'].queryset = none_rosters
            self.base_fields['winners'].queryset = none_rosters
            self.fields['winners'].queryset = none_rosters
            pass
        else:
            self.base_fields['rosters'].queryset = Roster.objects
            self.fields['rosters'].queryset = Roster.objects
            self.base_fields['winners'].queryset = Roster.objects
            self.fields['winners'].queryset = Roster.objects

    def clean_rosters(self):
        rosters = self.cleaned_data['rosters']
        if not rosters:
            return rosters

        general_pts = rosters[0].pts
        for i in rosters:
            if i.pts != general_pts:
                raise forms.ValidationError(
                    _(
                        'You can not write battle reports which has '
                        'rosters that differ with pts field'
                    )
                )
        return rosters

    def clean(self):
        cleaned_data = self.cleaned_data
        rosters = self.cleaned_data.get('rosters', None)
        winners = self.cleaned_data.get('winners', None)
        layout = self.cleaned_data.get('layout', None)
        if rosters and winners:
            for winner in winners:
                if winner not in rosters:
                    msg = _(
                        'You must choose winner\'s roster id within '
                        'rosters\' ids you passed'
                    )
                    self._errors['winners'] = ErrorList([msg])
                    del cleaned_data['winners']

        if rosters and layout:
            s = sum([int(i) for i in layout.split('vs')])
            if len(rosters) != s:
                msg = _(
                    'Number of players and layout must exact by '
                    'the amount of whole players'
                )
                self._errors['layout'] = ErrorList([msg])
                del cleaned_data['layout']

        if winners and layout:
            teams = [int(i) for i in layout.split('vs')]
            if len(winners or []) > max(teams):
                self._errors['winners'] = _(
                    "You can not add more winners than %(amount)s"
                ) % {'amount': max(teams)}

        return cleaned_data

    def save(self, commit=True):
        if not self.instance.pk:
            self.instance.owner = self.request.user
        instance = super(AddBattleReportForm, self).save(commit)
        return instance

    class Meta:
        model = Report
        fields = (
            'title', 'mission', 'rosters', 'winners', 'layout',
            'deployment', 'comment')
        widgets = {
            'deployment': forms.Select(attrs={
                'data-class': 'chosen', 'class': 'form-control'})
        }

LAYOUT_CHOICES = (
    ('1vs1', _("Player versus Player")),
    ('2vs2', _("Two versus Two")),
    ('ffa', _("Free for all")),
)


class ReportForm(forms.ModelForm):
    required_css_class = 'required'
    layout = forms.ChoiceField(label=_("Layout"), choices=LAYOUT_CHOICES,
                               widget=forms.Select(attrs={
                                   'class': 'form-control',
                                   'data-toggle': 'select2'
                               }))

    def clean(self):
        winners = self.cleaned_data.get('winners', [])
        rosters = self.cleaned_data.get('rosters', [])
        if not all((winners, rosters)):
            return self.cleaned_data

        msg_lst = []
        for winner in winners:
            if winner not in rosters:
                msg = _("There's no such winner `%s` in rosters") % winner
                msg_lst.append(msg)
        if msg_lst:
            self._errors['winners'] = ErrorList(msg_lst)

        return self.cleaned_data

    class Meta:
        model = Report
        fields = ('title', 'layout', 'mission', 'rosters', 'winners',
                  'comment', 'is_draw')
        widgets = {
            'title': forms.TextInput(attrs=DEFAULT_ATTRS),
            'mission': forms.Select(attrs=SELECT2_ATTRS),
            'rosters': forms.SelectMultiple(attrs=SELECT2_ATTRS),
            'winners': forms.SelectMultiple(attrs=SELECT2_ATTRS),
            'comment': forms.Textarea(attrs={
                'class': 'form-control markitup'}),
        }


class DeepSearchRosterForm(RequestForm):
    player = forms.CharField(required=False)
    race = forms.CharField(required=False)
    pts = forms.CharField(required=False)
    title = forms.CharField(required=False)

    def clean_player(self):
        player = self.cleaned_data.get('player', None)

        if not player:
            return
        r = re.compile('[\w\s-]+')
        player = r.match(player).group()
        return player

    def clean_pts(self):
        raw_pts = self.cleaned_data.get('pts', None)
        if not raw_pts:
            return raw_pts
        try:
            r = re.compile('(>|>=|<=|==|<)(\d{1,5})')
            eq, pts = r.findall(raw_pts)[0]
            pts = int(pts)
            if pts > 20000:
                raise forms.ValidationError(
                    _(
                        'Where is no such rosters which have more '
                        'than 20k points'
                    )
                )
            return raw_pts
        except (IndexError, ):
            return raw_pts
        except:
            raise forms.ValidationError(
                _('You should pass only int values through "pts" field'))


class AddRosterForm(RequestForm):
    RACE_CHOICES = [
        # (i.id, i.name)
        # for i in Side.objects.all().exclude(
        #     name__iexact='none').order_by('id')
    ]
    RACE_CHOICES.insert(0, (0, u'------'))
    title = forms.CharField(label=_("Title"))
    player = forms.RegexField(regex=re.compile(r'^[\w\s-]+$', re.U),
                              required=False)
    roster = forms.CharField(widget=TinyMkWidget(
        attrs={'disable_user_quote': True, 'rows': 20, 'cols': '60'}))
    race = forms.ChoiceField(choices=RACE_CHOICES, initial=(0, u'------'))
    custom_race = forms.RegexField(regex=re.compile(r'[\w\s-]+', re.U),
                                   required=False)
    pts = forms.IntegerField()
    syntax = forms.ChoiceField(choices=settings.SYNTAX)
    comments = forms.CharField(widget=TinyMkWidget(
        attrs={'disable_user_quote': True}))
    hidden_syntax = forms.CharField(widget=forms.HiddenInput(),
                                    required=False)
    referer = forms.CharField(widget=forms.HiddenInput(),
                              required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        custom_race = cleaned_data.get('custom_race', None)
        race = cleaned_data.get('race', None)
        if not race:
            msg = _('Race field should contain exact value')
            self._errors['race'] = ErrorList([msg])
            del cleaned_data['race']
        if int(race) == 0 and not custom_race:
            msg = _(
                'You should to select one race from the race select '
                'field or type custom_race by your own'
            )
            self._errors['custom_race'] = ErrorList([msg])
            del cleaned_data['custom_race']
        return cleaned_data

    def clean_referer(self):
        referer = self.cleaned_data.get('referer', None)
        if not referer:
            referer = '/'
        return referer

    # kinda cheat ;)
    def clean_player(self):
        player = self.cleaned_data.get('player', None)
        if len(player) > 64:
            raise forms.ValidationError(
                _(
                    'You can not pass player\'s name that contains'
                    'more than 64 symbols'
                )
            )
        if not player:
            player = self.request.user.nickname
        return player

    def clean_pts(self):
        pts = self.cleaned_data.get('pts', None)
        if pts > 500:
            return pts
        else:
            raise forms.ValidationError(_(
                'The common pts should be greater than 500'))

REVISION_CHOICES = (
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
    (6, 6),
)


class AddRosterModelForm(RequestModelForm):
    required_css_class = 'required'
    revision = forms.ChoiceField(label=_("Revision"),
                                 choices=REVISION_CHOICES)
    codex = forms.ModelChoiceField(
        queryset=Codex.objects, required=True, empty_label=None,
        widget=forms.Select(attrs={'class': 'span5 chosen form-control'}),
        label=_('Codex')
    )

    class Meta:
        model = Roster
        exclude = ['owner', 'user', 'is_orphan', 'plain_side', ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'span5 form-control'}),
            'pts': forms.TextInput(attrs={'class': 'span5 form-control'}),
            'revision': forms.Select(attrs={
                'class': 'span5 chosen form-control'}),
            'roster': forms.Textarea(attrs={
                'class': 'markitup textile form-control'})
        }
        fields = [
            'title', 'pts', 'codex', 'revision', 'roster',
        ]

    def clean(self):
        cleaned_data = self.cleaned_data
        revision = cleaned_data.get('revision', None)
        codex = cleaned_data.get('codex', None)
        if not codex or not revision:
            return cleaned_data

        if not str(revision) in codex.revisions.split(','):
            msg = _(
                'There is no such revision in "%(unicode)s",'
                ' try to pass %(revisions)s as valid values'
            ) % {
                'unicode': codex.__unicode__(),
                'revisions': codex.revisions
            }
            self._errors['revision'] = ErrorList([msg])
            del cleaned_data['revision']
        return cleaned_data

    def clean_pts(self):
        pts = self.cleaned_data.get('pts', None)
        if pts > 500:
            return pts
        else:
            raise forms.ValidationError(
                _('The common pts should be greater than 500'))

    def clean_player(self):
        player = self.cleaned_data.get('player', None)
        if len(player) > 64:
            raise forms.ValidationError(
                _(
                    'You can not pass player\'s name that '
                    'contains more than 64 symbols'
                )
            )
        if not player:
            player = self.request.user.nickname
        return player


class RosterForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        attrs = {'class': 'form-control'}
        model = Roster
        fields = ('title', 'pts', 'roster', 'codex', 'revision')
        widgets = {
            'title': forms.TextInput(attrs=attrs),
            'pts': forms.NumberInput(attrs=attrs),
            'roster': forms.Textarea(attrs={'class': 'form-control markitup'}),
            'codex': forms.Select(
                attrs={'class': 'form-control', 'data-toggle': 'select2'}),
            'revision': forms.Select(
                attrs={'class': 'form-control', })
        }


class CodexForm(forms.ModelForm):
    required_css_class = 'required'
    side = forms.ModelChoiceField(
        label=_("Side"), queryset=Side.objects,
        widget=forms.Select(attrs={'class': 'form-control',
                                   'data-toggle': 'select2'}),
        required=False
    )
    army = forms.ModelChoiceField(
        label=_("Army"), queryset=Army.objects,
        widget=forms.Select(attrs={'class': 'form-control',
                                   'data-toggle': 'select2'}),
        required=False
    )

    def clean(self):
        cleaned_data = self.cleaned_data
        side = cleaned_data.get('side', None)
        army = cleaned_data.get('army')
        if not any((side, army)):
            msg = _("Anything from side or army should be selected")
            self._errors['side'] = ErrorList([msg])
        return cleaned_data

    class Meta:
        attrs = {'class': 'form-control'}
        model = Codex
        fields = ('side', 'army', 'title', 'revisions')
        widgets = {
            'title': forms.TextInput(attrs=attrs),
            'revisions': forms.TextInput(attrs=attrs)
        }
