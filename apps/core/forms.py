# coding: utf-8
from django import forms
from django.http import Http404
from django.db.models.query import QuerySet
from django.contrib.comments.models import Comment
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from apps.core.settings import SETTINGS as USER_DEFAULT_SETTINGS, SETTINGS_FIELDS as USER_DEFAULT_FIELDS
from apps.core.settings import SettingsFormOverload
from django.conf import settings
from apps.core import get_safe_message
from apps.core.widgets import TinyMkWidget
from apps.core.helpers import get_object_or_None
from django.contrib.contenttypes.models import ContentType

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
class CommentForm(forms.ModelForm):
    syntax = forms.ChoiceField(
        choices=settings.SYNTAX,required=False, widget=forms.HiddenInput,
        initial='textile'
    )
    comment = forms.CharField(widget=forms.Textarea)
    url = forms.CharField(required=False, widget=forms.HiddenInput)
    # TODO: clean it up
    #hidden_syntax = forms.CharField(widget=forms.HiddenInput(),required=False)
    #subscribe = forms.BooleanField(required=False)
    #unsubscribe = forms.BooleanField(required=False)
    # fuck it
    #app_n_model = forms.CharField(widget=forms.HiddenInput()) #required if we add the comment
    #obj_id = forms.CharField(widget=forms.HiddenInput()) #required the same as above
    content_type = forms.ModelChoiceField(
        queryset=ContentType.objects, empty_label=None,
        widget=forms.HiddenInput)
    object_pk = forms.CharField(widget=forms.HiddenInput)
    site = forms.ModelChoiceField(
        queryset=Site.objects, empty_label=None,
        widget=forms.HiddenInput, required=False
    )
    page = forms.RegexField(
        regex=re.compile(r'\d+|last',re.S|re.U), required=False, widget=forms.HiddenInput()
    )

    def __init__(self,*args,**kwargs):
        
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']

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
        # TODO: cleanup unessecary len word limitation
        #ten words
        #if len(comment.split(' '))<10:
        #    raise forms.ValidationError(_('You should write more than 10 words for a comment'))
        
        return comment

    def clean_syntax(self):
        syntax = self.cleaned_data.get('syntax', '')
        if syntax:
            syntax_codes = [i[0] for i in settings.SYNTAX]
            if syntax in syntax_codes:
                return syntax
            else:
                # fallback to default
                syntax = settings.SYNTAX[0][0]
                #raise forms.ValidationError(_('You should choose correct syntax mode'))
    
        return syntax

    """
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
    """

    def clean_page(self):
        page = self.cleaned_data.get('page',None)
        if 'last' in page:
            return page

    def clean_app_n_model(self):
        app_n_model = self.cleaned_data['app_n_model']
        if not '.' in app_n_model:
            raise forms.ValidationError(_("app_n_model has invalid format"))
        if len(app_n_model.split('.')) > 2:
            raise forms.ValidationError(_("app_n_model should be written "
                "in right order: 'app.model'")
            )
        return app_n_model

    def clean(self):
        cd = self.cleaned_data
        # check site and overrides if it does not set
        site = self.cleaned_data.get('site') or None
        if not site:
            site = Site.objects.order_by('id')[0]
            self.cleaned_data['site'] = site
        return cd

    def save(self, commit=True):
        #self.instance.content_type = self.content_type
        #self.instance.object_pk = obj_id
        self.instance.site = self.cleaned_data['site']
        if not self.instance.pk:
            self.instance.user = self.request.user
        content_type = self.cleaned_data['content_type']
        comment = Comment.objects.filter(
            content_type=content_type,
            object_pk=self.instance.object_pk).order_by('-submit_date')

        from datetime import datetime
        now = datetime.now()

        instance = None
        #TODO: make this more flexible
        if comment and not self.instance.pk: #exists
            comment = comment[0]
            if comment.user == self.request.user and comment.comment != self.instance.comment: #is equal
                #new comment and not a dublicate
                comment.comment += "\n"+ self.instance.comment
                #comment.submit_date = now
                ip = self.request.META.get('REMOTE_ADDR', '')
                if ip: comment.ip_address = ip
                if commit:
                    comment.save()
                return comment
            else:
                if comment.user == self.request.user:
                    return comment
                instance = super(CommentForm, self).save(commit)
                return instance
        instance = super(CommentForm, self).save(commit)
        return instance

    class Meta:
        model = Comment
        fields = (
            'comment', 'page', 'syntax',
            'url', 'site', 'content_type', 'object_pk'
        )


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
                action = model.actions[int(action)]
                return action(self.request, _qset, model, **kwargs)
            else:
                raise ObjectDoesNotExist, "form.is_valid should be ran fist"

        def __init__(self, *args, **kwargs):
            self.request = request
            if args:
                #blocking out users without permissions we need
                if not self.request.user.has_perms(permissions):
                    raise Http404('Your user does not have permissions you need to complete this operation.')
            super(_ActionForm, self).__init__(*args, **kwargs)
    return _ActionForm

class ActionForm(forms.Form):
    items = forms.ModelMultipleChoiceField(queryset=[], widget=forms.MultipleHiddenInput())
    action = forms.ChoiceField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        model = kwargs['model']
        qset = kwargs['qset']
        del kwargs['qset']
        del kwargs['model']
        self.base_fields['items'].queryset = qset
        _actions = []
        for x in range(0, len(model.actions)):
            _actions.append((x, x))
        self.base_fields['action'].choices = _actions
        del _actions
        super(ActionForm, self).__init__(*args, **kwargs)

class ActionApproveForm(ActionForm):
    approve = forms.BooleanField(label=_('Approve'), required=True,
        help_text=_('Yes, i approve'))   

class BruteForceCheck(object):
    """ depents on RequestModelForm """
    def __init__(self, *args, **kwargs):
        super(PasswordRestoreForm, self).__init__(*args, **kwargs)
        if all(self.data or (None, )):
            if not hasattr(self, 'request'):
                raise ImproperlyConfigured("You should add request")

    def save(self, commit=True):
        super(BruteForceCheck, self).save(commit)
        if 'brute_force_iter' in self.request.session:
            del self.request.session['brute_force_iter']
            self.request.session.save()

    def is_valid(self, *args, **kwargs):
        super(PasswordRestoreForm, self).is_valid(*args, **kwargs)
        if not self.is_valid():
            self.request['brute_force_iter'] = \
                self.request.get('brute_force_iter', 0) + 1
