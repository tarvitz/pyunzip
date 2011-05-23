# coding: utf-8
from apps.core import get_safe_message
from apps.core.helpers import get_object_or_none
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from apps.core.forms import RequestForm, RequestModelForm
from django.conf import settings
from apps.core.widgets import TinyMkWidget
from apps.core.helpers import get_content_type
from apps.wh.models import Side
from django.forms.util import ErrorList
from apps.tabletop.models import Mission, Roster, BattleReport, Codex
from apps.tabletop import fields
import re

from apps.wh.models import Fraction, Side, Army
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
                    self.base_fields['army'].queryset = Army.objects.filter(pk=POST['army'])
        super(AddCodexModelForm, self).__init__(*args, **kwargs)
    
    def save(self, *args, **kwargs):
        super(AddCodexModelForm, self).save(*args, **kwargs)

class AddBattleReportForm(RequestForm):
    title = forms.CharField()
    rosters = forms.RegexField(regex=re.compile('(\d+)(,)'))
    winner = forms.IntegerField()
    _mission_choices = [(i.id,'%s:%s' % (i.game.codename,i.title)) for i in Mission.objects.all()]
    mission = forms.ChoiceField(choices=_mission_choices)
    layout = forms.RegexField(regex=re.compile('^\d{1}vs\d{1}$'))
    syntax = forms.ChoiceField(choices=settings.SYNTAX)
    hidden_syntax = forms.CharField(widget=forms.HiddenInput(),required=False)
    comment = forms.CharField(widget=TinyMkWidget(attrs={'disable_user_quote':True}))
    next = forms.CharField(required=False,widget=forms.HiddenInput()) # could it be dangerous ?
    
    def clean_rosters(self):
        rosters_raw = self.cleaned_data['rosters']
        rosters = [int(i) for i in rosters_raw.split(',')]
        r = list()
        for i in rosters:
            r.append(get_object_or_none(Roster,id=int(i)))
            if not r[len(r)-1]:
                raise forms.ValidationError(_('There\'s no roster with "%i" id' % int(i)))
        general_pts = r[0].pts
        for i in r:
            if i.pts != general_pts:
                raise forms.ValidationError(_('You can not write battlereports which has rosters that differ with pts field'))
        #returns int list
        return rosters
    
    def clean_winner(self):
        winner_id = self.cleaned_data['winner']
        winner = get_object_or_none(Roster,id=winner_id)
        if winner:
            return winner
        else:
            raise forms.ValidationError(_('There\'s no roster with such id'))
    
    def clean_mission(self):
        mission_id = self.cleaned_data['mission']
        mission = get_object_or_none(Mission,id=mission_id)
        if mission:
            return mission
        else:
            raise forms.ValidationError(_('There\'s no mission with such id'))

    def clean(self):
        cleaned_data = self.cleaned_data
        rosters = self.cleaned_data.get('rosters',None)
        winner = self.cleaned_data.get('winner',None)
        layout = self.cleaned_data.get('layout',None)
        if rosters and winner:
            if not winner.id in rosters:
                msg = _('You must choose winner\'s roster id within rosters\' ids you passed')
                self._errors['winner'] = ErrorList([msg])
                del cleaned_data['winner']
        if rosters and layout:
            s = sum([int(i) for i in layout.split('vs')])
            if len(rosters) != s:
                msg = _('Number of players and layout must exact by the amount of whole players')
                self._errors['layout'] = ErrorList([msg])
                del cleaned_data['layout']

        return cleaned_data

class AddBattleReportModelForm(RequestModelForm):
    required_css_class='required'
    search_rosters = forms.CharField(required=False, label=_('Search rosters'),
        help_text=_('If you do not see rosters you need below you may search them'))
    ids = Roster.objects.all()[0:10]
    rosters_choice = forms.ModelMultipleChoiceField(queryset=Roster.objects.filter(pk__in=ids),
        help_text=_("You can add this rosters to battle report"),
        label=_('Available rosters'),
        required=False)
    del ids
    users = forms.ModelMultipleChoiceField(queryset=Roster.objects.none(),
        label=_('Rosters'))
    winner = forms.ModelChoiceField(queryset=Roster.objects.none(), required=False)
    layout = forms.RegexField(regex=re.compile(r'^[\d+vs]+',re.M),required=True,
        help_text=_('Game layout, for example 2vs2, 1vs1, 1vs1vs1, 2vs1vs1 etc.'))
    comment = forms.CharField(widget=TinyMkWidget(attrs={'disable_user_quote':True,
        'disable_syntax': True})) 
  
    class Meta:
        model = BattleReport
        fields = ('title', 'layout','mission', 'syntax', 'search_rosters',
            'rosters_choice', 'users', 'winner', 'comment')
        exclude = ['owner', 'published', 'approved', 'ip_address',]
   
    def __init__(self, *args, **kwargs):
        if 'instance' in kwargs:
            instance = kwargs['instance']
            #what do we have when we want to edit battle report ;)
            if instance:
                if instance.users.all():
                    self.base_fields['users'].queryset = Roster.objects.filter(pk__in=(
                        instance.users.all()))
                    self.base_fields['winner'].queryset = Roster.objects.filter(pk__in=(
                        instance.users.all()))
        
        #checking up for valid value existance
        if args:
            if 'users' in args[0]:
                plain_users = args[0].getlist('users')
                self.base_fields['users'].queryset = Roster.objects.filter(id__in=(plain_users))
            if 'winner' in args[0]:
                plain_winner = args[0]['winner']
                if plain_winner:
                    self.base_fields['winner'].queryset = Roster.objects.filter(id=plain_winner)
        super(AddBattleReportModelForm, self).__init__(*args, **kwargs)
    

    def clean(self):
        cleaned_data = self.cleaned_data
        layout = cleaned_data.get('layout', None)
        users = cleaned_data.get('users', None)
        if layout and users:
            l = sum([int(l) for l in layout.split('vs') if l ])
            if len(users) != l:
                msg =_('You should set right layout, for example 2vs2, 3vs1, number of players should be equal to number of rosters you\'ve passed')
                self._errors['users'] = ErrorList([msg])
                del cleaned_data['users']
        return cleaned_data

    def clean_layout(self):
        layout = self.cleaned_data['layout']
        l = sum([int(l) for l in layout.split('vs') if l])
        if l > 10:
            raise forms.ValidationError(_('10 players is absolute maximum, do not try to add layout with more players, it\'s strickly forbidden'))
        return layout
   
class DeepSearchRosterForm(RequestForm):
    player = forms.CharField(required=False)
    race = forms.CharField(required=False)
    pts = forms.CharField(required=False)
    title = forms.CharField(required=False)
    
    def clean_player(self):
        player = self.cleaned_data.get('player',None)
        
        if not player: return
        r = re.compile('[\w\s-]+')
        player = r.match(player).group()
        #print player
        return player

    def clean_pts(self):
        raw_pts = self.cleaned_data.get('pts',None)
        if not raw_pts: return raw_pts
        try:
            r = re.compile('(>|>=|<=|==|<)(\d{1,5})')
            eq,pts = r.findall(raw_pts)[0]
            pts = int(pts)
            if pts>20000:
                raise forms.ValidationError(_('Where is no such rosters which have more than 20k points'))
            return raw_pts
        except (IndexError):
            return raw_pts
        except:
            raise forms.ValidationError(_('You should pass only int values through "pts" field'))

class AddRosterForm(RequestForm):
    RACE_CHOICES =  [(i.id,i.name)for i in Side.objects.all().exclude(name__iexact='none').order_by('id')]
    RACE_CHOICES.insert(0,(0,'------'))
    title = forms.CharField()
    player = forms.RegexField(regex=re.compile(r'^[\w\s-]+$',re.U),required=False)
    roster = forms.CharField(widget=TinyMkWidget(attrs={'disable_user_quote':True,'rows':20,'cols':'60'}))
    race = forms.ChoiceField(choices=RACE_CHOICES,initial=(0,'------'))
    custom_race = forms.RegexField(regex=re.compile(r'[\w\s-]+',re.U),required=False)
    pts = forms.IntegerField()
    syntax = forms.ChoiceField(choices=settings.SYNTAX)
    comments = forms.CharField(widget=TinyMkWidget(attrs={'disable_user_quote':True}))
    hidden_syntax = forms.CharField(widget=forms.HiddenInput(),required=False)
    referer = forms.CharField(widget=forms.HiddenInput(),required=False)

    def clean(self):
        cleaned_data = self.cleaned_data
        custom_race = cleaned_data.get('custom_race',None)
        race = cleaned_data.get('race',None)
        if not race:
            msg = _('Race field should contain exact value')
            self._errors['race'] = ErrorList([msg])
            del cleaned_data['race']
        if int(race) == 0 and not custom_race:
            msg = _('You should to select one race from the race select field or type custom_race by your own')
            self._errors['custom_race'] = ErrorList([msg])
            del cleaned_data['custom_race']
        return cleaned_data
    
    def clean_referer(self):
        referer = self.cleaned_data.get('referer',None)
        if not referer:
            referer = '/'
        return referer

    #kinda cheat ;)
    def clean_player(self):
        player = self.cleaned_data.get('player',None)
        if len(player)>64:
	    raise forms.ValidationError(_('You can not pass player\'s name that contains more than 64 symbols'))
        if not player:
            player = self.request.user.nickname
        return player

    def clean_pts(self):
        pts = self.cleaned_data.get('pts',None)
        if pts>500:
            return pts
        else:
            raise forms.ValidationError(_('The common pts should be greater than 500'))

class AddRosterModelForm(forms.ModelForm):
    required_css_class = 'required'
    class Meta:
        model = Roster
        exclude = ['owner', 'user', 'is_orphan', 'plain_side']
        widgets = {
            'comments': TinyMkWidget(attrs={'disable_user_quote': True}),
            'roster': TinyMkWidget(attrs={'disable_user_quote': True})
        }
        fields = ['title', 'player', 'pts', 'syntax', 'codex', 'custom_codex', 'revision', 'roster', 'comments' ]
    
    def clean(self):
        cleaned_data = self.cleaned_data
        revision = cleaned_data.get('revision', None)
        codex = cleaned_data.get('codex', None)
        if not codex or not revision: return cleaned_data
        if not str(revision) in codex.revisions.split(','):
            msg = _('There is no such revision in "%s", try to pass %s as valid values' %
                (codex.__unicode__(), codex.revisions))
            self._errors['revision'] = ErrorList([msg])
            del cleaned_data['revision']
        return cleaned_data

    def clean_pts(self):
        pts = self.cleaned_data.get('pts', None)
        if pts > 500:
            return pts
        else:
            raise forms.ValidationError(_('The common pts should be greater than 500'))
    
    def clean_player(self):
        player = self.cleaned_data.get('player',None)
        if len(player)>64:
	    raise forms.ValidationError(_('You can not pass player\'s name that contains more than 64 symbols'))
        if not player:
            player = self.request.user.nickname
        return player

