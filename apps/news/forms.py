# coding: utf-8
import re

from apps.news.models import Category as NewsCategory, Meating, Event

from django import forms
from django.utils.translation import ugettext_lazy as _
from apps.core.forms import RequestModelForm
from django.conf import settings
from apps.core.widgets import TinyMkWidget, DateTimePickerInput
from apps.news.models import News
from django.core.exceptions import ImproperlyConfigured


class AddNewsForm(forms.Form):
    author = forms.RegexField(regex=re.compile(r'[\w\s-]+',re.U),required=True)
    content = forms.CharField(widget=forms.Textarea())
    approved = forms.BooleanField(required=False)


class ArticleModelForm(RequestModelForm):
    required_css_class = 'required'
    author = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    next = forms.CharField(widget=forms.HiddenInput(), required=False)
    hidden_syntax = forms.CharField(widget=forms.HiddenInput(), required=False)
    approved = forms.BooleanField(
        initial=False, required=False, label=_("approved?"),
        help_text=_("marks if the article would be approved")
    )

    def __init__(self, *args, **kwargs):
        super(ArticleModelForm, self).__init__(*args, **kwargs)
        if not self.request.user.has_perm('news.edit_news'):
            if 'approved' in self.base_fields:
                del self.base_fields['approved']
            if 'approved' in self.fields:
                del self.fields['approved']

    def save(self, commit=True):
        can_edit = self.request.user.has_perm('news.edit_news')
        ip = self.request.META.get('REMOTE_ADDR', '127.0.0.1')
        self.instance.author = (
            self.instance.author or self.request.user.get_username()
        )
        if not self.instance.pk:
            self.instance.author_ip = ip
            #if can_edit:
            #    self.instance.approved = True
        else:
            self.instance.editor = self.request.user.nickname or self.request.user.username
        instance = super(ArticleModelForm, self).save(commit=commit)
        return instance

    class Meta:
        model = News
        fields = ['title', 'author', 'category', 'syntax', 'content', 'approved', 'url']
        exclude = ['editor', 'author_ip', 'is_event', 'date',

        ]
        widgets = {
            'content': forms.Textarea,
            'syntax': forms.HiddenInput,
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control chosen'}),
            'url': forms.TextInput(attrs={'class': 'form-control'})
        }

class ArticleStatusForm(forms.ModelForm):
    resend = forms.BooleanField(
        initial=True, label=_("send notification"),
        help_text=_('sends notification to user email'),
        required=False
    )
    class Meta:
        model = News
        fields = ('status', 'reason', 'approved', 'resend')
        widgets = {
            'reason': forms.Textarea(attrs={'cols': '10', 'rows': 5})
        }

class ArticleForm(forms.Form):
    required_css_class='required'
    categories = NewsCategory.objects.all()
    CATEGORIES = list()
    for c in categories:
        CATEGORIES.append((c.id, c.name))
    title = forms.CharField()
    author = forms.RegexField(regex=re.compile(r'[\w\s-]+',re.U),required=False)
    editor = forms.RegexField(regex=re.compile(r'[\w\s-]+',re.U),required=False)
    url = forms.URLField(required=False)
    #head_content = forms.CharField(widget=forms.Textarea(),required=False)
    content = forms.CharField(widget=TinyMkWidget(attrs={'disable_syntax':False,
        'disable_user_quote': True}))
    category = forms.ChoiceField(choices=CATEGORIES)
    attachment = forms.FileField(required=False)
    syntax = forms.ChoiceField(choices=settings.SYNTAX)
    hidden_syntax = forms.CharField(widget=forms.HiddenInput(),required=False)

    #recieving all request :)
    def __init__(self, *args, **kwargs):
                if 'request' in kwargs:
                        self.request = kwargs['request']
                        del kwargs['request']
                super(ArticleForm, self).__init__(*args, **kwargs)

    #def clean_head_content(self):
    #    head_content = self.cleaned_data.get('head_content','')
    #    if len(head_content)>1000:
    #        raise forms.ValidationError(_("You can not use more than 1000 symbols within headline news editing, please shortage the head of the news"))
    #    return get_safe_message(head_content)

    def clean_content(self):
        content = self.cleaned_data.get('content','')
        #content = get_safe_message(content)
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

class AddMeatingForm(forms.ModelForm):
    required_css_class = 'required'
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(AddMeatingForm, self).__init__(*args, **kwargs)
        if self.data:
            if not hasattr(self, 'request'):
                raise ImproperlyConfigured("You should pass request as keyword param to proceed")

    def clean_author_ipv4(self):
        ipv4 = self.cleaned_data['ipv4']
        if not ipv4:
            ipv4 = '127.0.0.1'
        return ipv4

    def save(self, commit=False):
        self.instance.owner = self.request.user
        self.instance.author_ipv4 = self.request.META.get('REMOTE_ADDR', '127.0.0.1')
        if self.request.user.has_perm('news.add_meating') or\
            self.request.user.has_perm('news.change_meating'):
            self.instance.is_approved = True
        return super(AddMeatingForm, self).save(commit=commit)

    class Meta:
        model = Meating
        exclude = ['created_on', 'updated_on', 'is_approved',
            'author_ipv4', 'author_ipv6', 'owner', 'members',]


class EventForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        attrs ={'class': 'form-control'}
        model = Event
        widgets = {
            'date_start': DateTimePickerInput(
                format='%Y-%m-%d %H:%M',
                attrs={'class': 'form-control', 'klass': 'col-lg-4'}
            ),
            'date_end': DateTimePickerInput(
                format='%Y-%m-%d %H:%M',
                attrs={'class': 'form-control', 'klass': 'col-lg-4'}
            ),
            'content': forms.Textarea(
                attrs={'class': 'form-control markitup'}
            ),
            'title': forms.TextInput(attrs),
            'type': forms.Select(attrs={'class': 'form-control chosen'}),
            'league': forms.Select(attrs={'class': 'form-control chosen'}),
            'place': forms.Select(attrs={'class': 'form-control chosen'}),
        }
        fields = ('title', 'content', 'place', 'date_start', 'date_end',
                  'league', 'type', 'is_all_day')

    class Media:
        js = (
            settings.STATIC_URL + "components/moment/min/moment.min.js",
            settings.STATIC_URL + "components/"
            "eonasdan-bootstrap-datetimepicker/"
            "src/js/locales/bootstrap-datetimepicker.ru.js",
            settings.STATIC_URL + "components/"
            "eonasdan-bootstrap-datetimepicker/"
            "build/js/bootstrap-datetimepicker.min.js",
        )
        css = {
            'all': (
                settings.STATIC_URL + 'components/'
                "eonasdan-bootstrap-datetimepicker/build/css/"
                "bootstrap-datetimepicker.min.css",
            )
        }


class EventParticipateForm(forms.ModelForm):
    agree = forms.BooleanField(label=_("Yes, I agree"), required=True)

    class Meta:
        model = Event
        fields = ()