
from django import forms
from django.utils.translation import ugettext_lazy as _
from apps.core.settings import SETTINGS as USER_DEFAULT_SETTINGS, SETTINGS_FIELDS as USER_DEFAULT_FIELDS
from apps.core.settings import SettingsFormOverload
from django.conf import settings
from apps.core import get_safe_message
from apps.core.widgets import TinyMkWidget

class RequestForm(forms.Form):
	def __init__(self, *args, **kwargs):
                if 'request' in kwargs:
                        self.request = kwargs['request']
                        del kwargs['request']
                super(RequestForm, self).__init__(*args, **kwargs)

class AddEditCssForm(RequestForm):
    css = forms.CharField(widget=forms.Textarea())

class ApproveActionForm(forms.Form):
     url = forms.CharField(widget=forms.HiddenInput())

class SearchForm(forms.Form):
    query = forms.CharField()

    def clean(self):
        return self.cleaned_data

class SettingsForm(RequestForm):
    #objects_on_page = forms.IntegerField(_('Objects on page'),required=True)
    
    def __init__(self,*args,**kwargs):
        #override the settings and so on
        for k in USER_DEFAULT_SETTINGS.keys():
            self.base_fields.update(USER_DEFAULT_FIELDS)
            try:
                self.base_fields[k].initial = USER_DEFAULT_SETTINGS[k]
            except:
                pass
        super(RequestForm,self).__init__(*args,**kwargs)

SettingsForm.__bases__ = SettingsForm.__bases__ + (SettingsFormOverload,)

#duplicates with files.forms need more 'usable' interface for comments
class CommentForm(forms.Form):
    syntax = forms.ChoiceField(choices=settings.SYNTAX,required=False)
    comment = forms.CharField(widget=TinyMkWidget())
    url = forms.CharField(required=False,widget=forms.HiddenInput())
    hidden_syntax = forms.CharField(widget=forms.HiddenInput(),required=False)
    subscribe = forms.BooleanField(required=False)
    unsubscribe = forms.BooleanField(required=False)
    app_n_model = forms.CharField(required=False,widget=forms.HiddenInput()) #required if we add the comment
    obj_id = forms.CharField(required=False,widget=forms.HiddenInput()) #required the same as above
    page = forms.IntegerField(required=False,widget=forms.HiddenInput())

    def __init__(self,*args,**kwargs):
        
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        #if 'app_n_model' in kwargs['request']:
        #    self.base_fields['app_n_model'].initial = kwargs['app_n_model']
        #    del kwargs['request']
        #if 'obj_id' in kwargs:
        #    self.base_fields['obj_id'].initial = kwargs['obj_id']
        #    del kwargs['obj_id']

        #overriding url by default if not set
        if hasattr(self,'request'):
            #if there clean value we set it up
            self.base_fields['url'].initial = "%s/%s" % (self.request.META.get('HTTP_HOST','http://localhost'),
                    self.request.META.get('INFO_PATH',''))
        
        super(CommentForm,self).__init__(*args,**kwargs)
    
    def clean_comment(self):
        comment = self.cleaned_data['comment']
        comment = get_safe_message(comment)
        if not comment:
            raise forms.ValidationError(_('You should write something'))
        
        if len(comment) > 10000:
            raise forms.ValidationError(_('You can not post over 10000 symbols within your comment!'))
       
        #staff and super user is allowed to post
        #any shit they want o_O
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return comment
        #ten words
        if len(comment.split(' '))<10:
            raise forms.ValidationError(_('You should write more than 10 words for a comment'))
        
        return comment

    def clean_syntax(self):
        syntax = self.cleaned_data.get('syntax','')
        if syntax:
            syntax_codes = [i[0] for i in settings.SYNTAX]
            if syntax in syntax_codes:
                return syntax
            else:
                raise forms.ValidationError(_('You should choose correct syntax mode'))
        else:
            return syntax
    
    def clean_hidden_syntax(self):
        syntax = self.cleaned_data.get('hidden_syntax','')
        if syntax:
            syntax_codes = [i[0] for i in settings.SYNTAX]
            if syntax in syntax_codes:
                return syntax
            else:
                raise forms.ValidationError(_('Syntax value should be correct'))
        else:
            return syntax

