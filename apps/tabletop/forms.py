# coding: utf-8
from django import forms
from django.utils.translation import (
    ugettext_lazy as _,
    pgettext_lazy
)

from apps.core.forms import RequestForm, RequestModelForm
from django.conf import settings
from apps.core.widgets import TinyMkWidget


from django.forms.util import ErrorList
from apps.tabletop.models import Mission, Roster, BattleReport, Codex

import re

from apps.wh.models import Side, Army


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
        #regex=re.compile('^[\w\d\ \-\_\.]+$'),
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
        #returns int list
        return rosters

    def clean(self):
        cleaned_data = self.cleaned_data
        rosters = self.cleaned_data.get('rosters', None)
        winners = self.cleaned_data.get('winners', None)
        layout = self.cleaned_data.get('layout', None)
        if rosters and winners:
            for winner in winners:
                if not winner in rosters:
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
        model = BattleReport
        fields = (
            'title', 'mission', 'rosters', 'winners', 'layout',
            'deployment', 'comment')
        widgets = {
            'deployment': forms.Select(attrs={
                'data-class': 'chosen', 'class': 'form-control'})
        }


class AddBattleReportModelForm(RequestModelForm):
    required_css_class = 'required'
    search_rosters = forms.CharField(
        required=False, label=_('Search rosters'),
        help_text=_(
            'If you do not see rosters you need below you may search them'))
    ids = Roster.objects.all()[0:10]
    rosters_choice = forms.ModelMultipleChoiceField(
        queryset=Roster.objects.filter(pk__in=ids),
        help_text=_("You can add this rosters to battle report"),
        label=_('Available rosters'),
        required=False
    )
    del ids
    users = forms.ModelMultipleChoiceField(queryset=Roster.objects.none(),
                                           label=_('Rosters'))
    winner = forms.ModelChoiceField(queryset=Roster.objects.none(),
                                    required=False)
    layout = forms.RegexField(
        regex=re.compile(r'^[\d+vs]+', re.M), required=True,
        help_text=_(
            'Game layout, for example 2vs2, 1vs1, 1vs1vs1, 2vs1vs1 etc.'))
    comment = forms.CharField(
        widget=TinyMkWidget(
            attrs={'disable_user_quote': True, 'disable_syntax': True}))

    class Meta:
        model = BattleReport
        fields = ('title', 'layout', 'mission', 'syntax', 'search_rosters',
                  'rosters_choice', 'users', 'winner', 'comment')
        exclude = ['owner', 'published', 'approved', 'ip_address', ]

    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            instance = kwargs['instance']
            #what do we have when we want to edit battle report ;)
            if instance:
                if instance.users.all():
                    self.base_fields['users'].queryset = Roster.objects.filter(
                        pk__in=(instance.users.all()))
                    self.base_fields['winner'].queryset = \
                        Roster.objects.filter(pk__in=(instance.users.all()))

        #checking up for valid value existance
        if args:
            if 'users' in args[0]:
                plain_users = args[0].getlist('users')
                self.base_fields['users'].queryset = Roster.objects.filter(
                    id__in=(plain_users, ))
            if 'winner' in args[0]:
                plain_winner = args[0]['winner']
                if plain_winner:
                    self.base_fields['winner'].queryset = \
                        Roster.objects.filter(id=plain_winner)
        super(AddBattleReportModelForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        layout = cleaned_data.get('layout', None)
        users = cleaned_data.get('users', None)
        if layout and users:
            l = sum([int(l) for l in layout.split('vs') if l])
            if len(users) != l:
                msg = _(
                    'You should set right layout, for example 2vs2, '
                    '3vs1, number of players should be equal to number '
                    'of rosters you\'ve passed'
                )
                self._errors['users'] = ErrorList([msg])
                del cleaned_data['users']
        return cleaned_data

    def clean_layout(self):
        layout = self.cleaned_data['layout']
        l = sum([int(l) for l in layout.split('vs') if l])
        if l > 10:
            raise forms.ValidationError(_(
                '10 players is absolute maximum, do not try to'
                ' add layout with more players, it\'s strickly forbidden'
            ))
        return layout


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
        #print player
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
        (i.id, i.name) for i in Side.objects.all().exclude(
            name__iexact='none').order_by('id')
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

    #kinda cheat ;)
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