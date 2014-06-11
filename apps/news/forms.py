# coding: utf-8
from apps.news.models import Event

from django import forms
from django.utils.translation import ugettext_lazy as _
from apps.core.forms import RequestModelForm
from django.conf import settings
from apps.core.widgets import DateTimePickerInput
from apps.news.models import News


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
        # can_edit = self.request.user.has_perm('news.edit_news')
        ip = self.request.META.get('REMOTE_ADDR', '127.0.0.1')
        self.instance.author = (
            self.instance.author or self.request.user.get_username()
        )
        if not self.instance.pk:
            self.instance.author_ip = ip
            #if can_edit:
            #    self.instance.approved = True
        else:
            self.instance.editor = (
                self.request.user.nickname or self.request.user.username)
        instance = super(ArticleModelForm, self).save(commit=commit)
        return instance

    class Meta:
        model = News
        fields = ['title', 'author', 'category', 'syntax', 'content',
                  'approved', 'url']
        exclude = ['editor', 'author_ip', 'is_event', 'date', ]
        widgets = {
            'content': forms.Textarea,
            'syntax': forms.HiddenInput,
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control chosen'}),
            'url': forms.TextInput(attrs={'class': 'form-control'})
        }


class EventForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        attrs = {'class': 'form-control'}
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