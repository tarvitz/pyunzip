# coding: utf-8
from apps.core import get_safe_message
from apps.core.helpers import get_object_or_none
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from apps.core.forms import RequestForm, RequestModelForm
from django.conf import settings
from apps.core.widgets import TinyMkWidget
from apps.wh.models import Side
from django.forms.util import ErrorList
from apps.tabletop.models import Mission,Roster, BattleReport
from apps.tabletop import fields
import re

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
    search_rosters = forms.CharField(required=False, label=_('Search rosters'),
        help_text=_('If you do not see rosters you need below you may search them'))
    ids = Roster.objects.all()[0:10]
    rosters_choice = forms.ModelMultipleChoiceField(queryset=Roster.objects.filter(pk__in=ids),
        help_text=_("You can add this rosters to battle report"),
        label=_('Available rosters'),
        required=False)
    del ids
    rosters = fields.NonCheckMultipleChoiceField(help_text=_('Chosen rosters'))
    winner_choice = fields.NonCheckChoiceField(
        choices=((-1, '-----'),),
        label=_('Winner'),
        help_text=_('Person who won the battle'))
    layout = forms.RegexField(regex=re.compile(r'^[\d+vs]+',re.M),required=True,
        help_text=_('Game layout, for example 2vs2, 1vs1, 1vs1vs1, 2vs1vs1 etc.'))
    comment = forms.CharField(widget=TinyMkWidget(attrs={'disable_user_quote':True,
        'disable_syntax': True})) 
    
    def clean(self):
        cleaned_data = self.cleaned_data
        layout = cleaned_data.get('layout', None)
        rosters = cleaned_data.get('rosters', None)
        if layout and rosters:
            l = sum([int(l) for l in layout.split('vs') if l ])
            if len(rosters) != l:
                msg =_('You should set right layout, for example 2vs2, 3vs1, number of players should be equal to number of rosters you\'ve passed')
                self._errors['rosters'] = ErrorList([msg])
                del cleaned_data['rosters']
        return cleaned_data
    def clean_layout(self):
        layout = self.cleaned_data['layout']
        l = sum([int(l) for l in layout.split('vs') if l])
        if l > 10:
            raise forms.ValidationError(_('10 players is absolute maximum, do not try to add layout with more players, it\'s strickly forbidden'))
        return layout
    def clean_winner_choice(self):
        wc = self.cleaned_data['winner_choice']
        winner = get_object_or_none(Roster, pk=wc)
        if not winner:
            raise forms.ValidationError(_('Such winner roster does not exist'))
        self.cleaned_data['winner_instance'] = winner
        return wc

    def clean_rosters(self):
        rosters = self.cleaned_data['rosters']
        try:
            rosters = [int(r) for r in rosters]
        except:
            raise forms.ValidationError(_('Rosters id\'s should be int type'))
        #pts = None
        self.cleaned_data['roster_instances'] = list()
        for r in rosters:
            roster = get_object_or_none(Roster, id=r)
            #if not pts: pts = roster.pts
            #if pts != roster.pts:
            #    raise forms.ValidationError(_('You should user rosters with equal pts'))
            if not roster:
                raise forms.ValidationError(_("Roster with id '%i' does not exist" % r))
                del self.cleaned_data['roster_instances']
            self.cleaned_data['roster_instances'].append(roster)
        return rosters

    class Meta:
        model = BattleReport
        fields = ('title', 'layout','mission', 'syntax', 'search_rosters',
            'rosters_choice', 'rosters','winner_choice','comment')
        exclude = ['owner','winner', 'published', 'approved', 'ip_address', 'users']
        
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
    roster = forms.CharField(widget=forms.Textarea(attrs={'rows':20,'cols':'60'}))
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
"""
class AddNewsForm(forms.Form):
    author = forms.CharField(required=True)
    content = forms.CharField(widget=forms.Textarea())
    approved = forms.BooleanField(required=False)

class ArticleForm(forms.Form):
    categories = NewsCategory.objects.all()
    CATEGORIES = list()
    for c in categories:
        CATEGORIES.append((c.id, c.name))
    title = forms.CharField()
    author = forms.CharField(required=False)
    editor = forms.CharField(required=False)
    url = forms.URLField(required=False)
    head_content = forms.CharField(widget=forms.Textarea(),required=False)
    content = forms.CharField(widget=TinyMkWidget(attrs={'disable_syntax':True,'disable_user_quote': True}))
    category = forms.ChoiceField(choices=CATEGORIES)
    attachment = forms.FileField(required=False)
    syntax = forms.ChoiceField(choices=(('markdown','markdown'),('bb-code','bb-code'),))
    hidden_syntax = forms.CharField(widget=forms.HiddenInput(),required=False)

    #recieving all request :)
    def __init__(self, *args, **kwargs):
                if 'request' in kwargs:
                        self.request = kwargs['request']
                        del kwargs['request']
                super(ArticleForm, self).__init__(*args, **kwargs)
    
    def clean_head_content(self):
        head_content = self.cleaned_data.get('head_content','')
        if len(head_content)>1000:
            raise forms.ValidationError(_("You can not use more than 1000 symbols within headline news editing, please shortage the head of the news"))
        return get_safe_message(head_content)

    def clean_content(self):
        content = self.cleaned_data.get('content','')
        content = get_safe_message(content)
        if len(content) > 20000:
            raise forms.ValidationError(_("You can not use more then 20000 symbols while you post article"))
        return content

    def clean(self):
        cleaned_data = self.cleaned_data
        author = cleaned_data.get('author','')
        if not author:
            author = self.request.user.nickname
            cleaned_data['author'] = author
        else:
            editor = self.request.user.nickname
            cleaned_data['editor'] = editor
        return cleaned_data

    def clean_attachment(self):
        attachment = self.cleaned_data.get('attachment','')
        if not attachment:
            #print attachment
            return None
        else:
            name = attachment.name
            #it's better to use type validation instead of ext validation
            try:
                ext = name[name.rindex('.')+1:]
            except ValueError:
                raise forms.ValidationError(_('Unknow type of file'))
            if not ext.lower() in ['zip','gz','bz2','gzip']:
                raise forms.ValidationError(_('Only zip files supported'))
            return attachment

class ApproveActionForm(forms.Form):
     url = forms.CharField(widget=forms.HiddenInput())
"""
