# coding: utf-8
from apps.news.models import Category as NewsCategory
from apps.core import get_safe_message
from django import forms
from django.utils.translation import ugettext_lazy as _
from apps.core.forms import RequestForm
from django.conf import settings
from apps.core.widgets import TinyMkWidget
import re
class AddNewsForm(forms.Form):
    author = forms.RegexField(regex=re.compile(r'[\w\s-]+',re.U),required=True)
    content = forms.CharField(widget=forms.Textarea())
    approved = forms.BooleanField(required=False)

class ArticleForm(forms.Form):
    categories = NewsCategory.objects.all()
    CATEGORIES = list()
    for c in categories:
        CATEGORIES.append((c.id, c.name))
    title = forms.CharField()
    author = forms.RegexField(regex=re.compile(r'[\w\s-]+',re.U),required=False)
    editor = forms.RegexField(regex=re.compile(r'[\w\s-]+',re.U),required=False)
    url = forms.URLField(required=False)
    head_content = forms.CharField(widget=forms.Textarea(),required=False)
    content = forms.CharField(widget=TinyMkWidget(attrs={'disable_syntax':False,'disable_user_quote': True}))
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
    
    def clean_author(self):
        author = self.cleaned_data['author']
        if not author: return ''
        author = re.match(r'[\w\s-]+',author,re.U).group()
        if author:
            return author
        else:
            raise forms.ValidationError(_('You can only use symbols spaces and "-" sign'))

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
