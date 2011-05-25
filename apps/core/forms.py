
from django import forms
from django.http import Http404
from django.db.models.query import QuerySet
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from apps.core.settings import SETTINGS as USER_DEFAULT_SETTINGS, SETTINGS_FIELDS as USER_DEFAULT_FIELDS
from apps.core.settings import SettingsFormOverload
from django.conf import settings
from apps.core import get_safe_message
from apps.core.widgets import TinyMkWidget
import re

class RequestModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(RequestModelForm, self).__init__(*args, **kwargs)

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
    page = forms.RegexField(regex=re.compile(r'\d+|last',re.S|re.U),required=False,widget=forms.HiddenInput())

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
        ally = user.ranks.filter(codename='Ally')
        if user.is_superuser or user.is_staff or ally:
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
    
    def clean_page(self):
        page = self.cleaned_data.get('page',None)
        if 'last' in page:
            return page

class SphinxSearchForm(forms.Form):
    query = forms.CharField(required=True)

def action_formset(qset, actions):
    """ taken within stackoverflow,
    form which allows the user to pick specified action to perform on a chosen
    subset of items from queryset"""
    
    class _ActionForm(forms.Form):
        items = forms.ModelMultipleChoiceField(queryset=qset)
        action = forms.ChoiceField(choices=[(None, '--------'),]+zip(actions, actions))

    return _ActionForm

def action_formset_ng(request, qset, model, permissions=[]):
    """ more useable generic action form """

    class _ActionForm(forms.Form): 
        items = forms.ModelMultipleChoiceField(queryset=qset)
        #_actions = [(s.short_description, s.short_description) for s in model.actions]
        _actions = []
        for x in range(0, len(model.actions)):
            _actions.append((x, model.actions[x].short_description))
        action = forms.ChoiceField(choices=[(None, '--------'),]+ _actions)
        
        del _actions

        def act(self, action, _qset, **kwargs):
            if hasattr(self, 'is_valid'):
                if action == 'None':
                    return _qset #return what do we got, nothing else
                action = model.actions.pop(int(action))
                return action(request, _qset, **kwargs)
            else:
                raise ObjectDoesNotExist, "form.is_valid should be ran fist"

        def __init__(self, *args, **kwargs):
            self.request = request
            if args:
                #blocking out users without permissions we need
                if not request.user.has_perms(permissions):
                    raise Http404('Your user does not have permissions you need to complete this operation.')
            super(_ActionForm, self).__init__(*args, **kwargs)
    return _ActionForm
