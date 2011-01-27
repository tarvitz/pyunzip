from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from apps.files.models import Version,Gallery
from apps.core import get_safe_message
from apps.files.helpers import is_zip_file
from PIL import Image
from cStringIO import StringIO
from apps.core.forms import RequestForm
from apps.core.widgets import TinyMkWidget
from django.conf import settings

#abstract forms
class IncomeFileForm(forms.Form):
    description = forms.CharField()
    file = forms.FileField()
#end of abstract forms
class FileUploadForm(IncomeFileForm):
    url = forms.URLField(required=False)

#default to DoW1
class ActionReplayForm(forms.Form):
    TYPE_CHOICES=(
        ('1','1vs1'),
        ('2','2vs2'),
        ('3','3vs3'),
        ('4','4vs4'),
        ('5',_('set')),
        ('0',_('non standard')),
    )
    WINNERS_CHOICES = list()
    for i in xrange(8): WINNERS_CHOICES.append(('%i' % (i+1),'team %i' % (i+1)))
    #TODO: Find out who to filter fields from view via outside request
    versions = Version.objects.order_by('-release_number','-patch') #kinda hack, because we should select all availble version to get passed the form :)
    name = forms.CharField()
    type = forms.ChoiceField(choices=TYPE_CHOICES)
    #hidden
    nonstd_layout = forms.CharField(required=False)
    teams = forms.CharField(required=False)
    races = forms.CharField()
    winners = forms.ChoiceField(choices=WINNERS_CHOICES,required=False)
    version = forms.ModelChoiceField(versions)
    comments = forms.CharField(widget=TinyMkWidget({}), required=False)
    is_set = forms.BooleanField(required=False)
    hidden_syntax = forms.CharField(required=False,widget=forms.HiddenInput())

    def clean_comments(self):
        comments = self.cleaned_data.get('comments','')
        comments = get_safe_message(comments)
        return comments

    #always set it to default
    def clean_hidden_syntax(self):
        syntax = self.cleaned_data.get('hidden_syntax','')
        if not syntax:
            return settings.SYNTAX[0][0]

    def clean(self):
        cleaned_data = self.cleaned_data
        nonstd_layout = cleaned_data.get('nonstd_layout')
        players = cleaned_data.get('teams')
        type = cleaned_data.get('type')
        winners = int(cleaned_data.get('winners'))
        is_set = int(cleaned_data.get('is_set'))
	print is_set, " :is_set"
        if is_set or is_set == 0: return cleaned_data #get exitin with 
        
        teams = self.cleaned_data['teams']
        metric = int(self.cleaned_data['type'])
	#with 0 value we should test both fields, this defined right some entries above
        if not is_set:
            if len(teams.split(',')) != (metric*2) and metric != 0:
                msg = _('You should type exact %i nicks separated with commas arranged by team.' % (metric*2))
                self._errors['teams'] = ErrorList([msg])
                del cleaned_data['teams']
        #clean winners:
        if int(type) != 0:
            if winners>2:
                msg = _('You should choose team 1 or team 2 as winners')
                self._errors['winners'] = ErrorList([msg])
                del cleaned_data['winners']
        if int(type) == 0:
            if not nonstd_layout:
                msg = _('This field should be filled with layout')
                self._errors['nonstd_layout'] = msg
                del cleaned_data['nonstd_layout']

            if winners>len(nonstd_layout.split('vs')):
                msg = _('You should choose team which is lesser one you\'ve chosen, for example team 1')
                self._errors['winners'] = ErrorList([msg])
                del cleaned_data['winners']
            if nonstd_layout and players:
                players = players.split(',')
                layout = nonstd_layout.split('vs')
                number_of_players = [int(i) for i in  layout ]
                if len(players)>sum(number_of_players):
                    #TODO: add fix for ....ing snicky bastards who tries use 0vs0 layout or negative nums
                    msg = _("The number of nicks is greater than the number of players. The should be equal")
                    self._errors['teams'] = ErrorList([msg])
                    del cleaned_data['nonstd_layout']
                    del cleaned_data['teams']
                if len(players)<sum(number_of_players):
                    msg = _("The number of players is greater then the number of nicks. The should be equal")
                    self._errors['nonstd_layout'] = ErrorList([msg])
                    del cleaned_data['nonstd_layout']
                    del cleaned_data['teams']
        return cleaned_data

    def clean_nonstd_layout(self):
        value = self.cleaned_data['nonstd_layout']
        value = value.lower()
        if not value: return ''
        try:
            value.index('vs')
        except ValueError:
            raise forms.ValidationError(_('Field should contain string with number of player separated with vs'))
        try:
            num = [int(i) for i in value.split('vs')]
        except ValueError:
            raise forms.ValidationError(_('It seems string value or null stands before or after \'vs\' delimiter'))
        if sum(num)>8:
            raise forms.ValidationError(_('The game does not support more than 8 players, and your amount of them equals %i' % sum(num)))
        return value
    """
#expired :)
    def clean_teams(self):
        value = self.cleaned_data['teams']
        metric = int(self.cleaned_data['type'])
        is_set = self.cleaned_data.get('is_set')
        #with 0 value we should test both fields, this defined right some entries above
        if not is_set:
            if len(value.split(',')) != (metric*2) and metric != 0:
                raise forms.ValidationError(_('You should type exact %i nicks separated with commas arranged by team.' % (metric*2)))
        return value
    """
    
    def clean_races(self):
        value = self.cleaned_data['races']
        if not value:
            raise forms.ValidationError(_('The field should be at least includes one race, for example space marines'))
        return value
class EditReplayForm(ActionReplayForm):
    url = forms.CharField(widget=forms.HiddenInput())
    hidden_syntax = forms.CharField(widget=forms.HiddenInput())
class UploadReplayForm(ActionReplayForm):
    replay = forms.FileField()

    def clean_replay(self):
        value = self.cleaned_data.get('replay','')
        if not value: return None
        #print value.name
        name = value.name
        #TODO: implement replay detection
        #type validation is realy sucks ;)
        """try:
            ext = name[name.rindex('.')+1:]
        except ValueError:
            raise forms.ValidationError(_('Unknown type of file'))
        if not ext.lower() in ['zip']:
            raise forms.ValidationError(_('This file should be zip extention type'))
        #validate zip
        if ext.lower() in 'zip':
            #check if it iz a zip file
            if not is_zip_file(value): 
                raise forms.ValidationError(_('This zip file is corrupt or broken'))
        """
        return value

    def clean(self):
        cleaned_data = self.cleaned_data
        is_set = cleaned_data.get('is_set',False)
        if is_set:
            replay = cleaned_data.get('replay','')
            if not is_zip_file(replay):
                msg = _("The set of replay pack should be packed as zip file!")
                self._errors['replay'] = ErrorList([msg])
                del cleaned_data['replay']
        return cleaned_data

class UploadImageForm(RequestForm):
    #FIXME
    #kindahack!
    choices = list()
    galleries = Gallery.objects.all()
    for g in galleries:
        choices.append((g.id,g.name))
    #endof kindahack

    image = forms.ImageField()
    title = forms.CharField()
    comments = forms.CharField(required=False)
    gallery = forms.ChoiceField(choices=choices)
    
    def clean_comments(self):
        comments = self.cleaned_data.get('comments','')
        comments = get_safe_message(comments)
        return comments

    def clean_image(self):
        user = self.request.user
        value = self.cleaned_data.get('image', '')
        if (value.size / 1024 / 1024) > 1:
            raise forms.ValidationError(_('Uploaded file should not be larger than 1Mb size'))
        file = ''
        for i in value.chunks(): file += i
        content = file
        if 'content-type' in value:
            main, sub = value['content-type'].split('/')
            if not (main == 'image' and sub in ['jpeg','gif','png', 'jpg']):
                raise forms.ValidationError(_('Jpeg, gif, png, jpg image only'))
        try:
            img = Image.open(StringIO(content))
            x,y = img.size
        except:
            raise forms.ValidationError(_('Upload a valid image. The file you uploaded was either not an image or a corrupted image.'))
        if not user.is_superuser or not user.is_staff:
            if x>2048 or y>2048:
                raise forms.ValidationError(_('Uploaded image should not be larger than 2048x1024 pixels'))
        return value

    def clean_gallery(self):
        value = self.cleaned_data.get('gallery')
        if not value:
            raise forms.ValidationError(_('Field should\'t be clean, if you have no gallery yet, please create one'))
        return value

class CommentForm(RequestForm):
    comment = forms.CharField(widget=forms.Textarea())

    def clean_comment(self):
        comment = self.cleaned_data['comment']
        comment = get_safe_message(comment)
        if not comment:
            raise forms.ValidationError(_('You should write something'))
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return comment
        if len(comment.split(' '))<10:
            raise forms.ValidationError(_('You should write more than 10 words for a comment'))
        return comment

class CreateGalleryForm(forms.Form):
    name  = forms.CharField()

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name)>100:
            raise forms.ValidationError(_('The length of gallery name was exceeded'))
        return name
