import re
from datetime import datetime

from django import forms
from django.forms.util import ErrorList
from django.forms.models import BaseInlineFormSet
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from apps.pybb.models import (
    Topic, Post, Profile, PrivateMessage, Poll, PollAnswer, PollItem
)
from apps.pybb import settings as pybb_settings


class AddPostForm(forms.ModelForm):
    name = forms.CharField(
        label=_('Subject'),
        widget=forms.TextInput(attrs={'class': 'span6 form-control'})
    )

    class Meta:
        model = Post
        fields = [
            #'markup',
            'body'
        ]
        widgets = {
            'markup': forms.Select(attrs={'class': 'span6 form-control'}),
            #'body': forms.Textarea(attrs={'class': 'span6'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.topic = kwargs.pop('topic', None)
        self.forum = kwargs.pop('forum', None)
        self.ip = kwargs.pop('ip', None)
        super(AddPostForm, self).__init__(*args, **kwargs)
        if self.topic:
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['name'].required = False

        self.fields.keyOrder = [
            #'markup',
            'body'
        ]
        if not self.topic:
            self.fields.keyOrder.insert(0, 'name')


    def save(self):
        if self.forum:
            topic = Topic(forum=self.forum,
                          user=self.user,
                          name=self.cleaned_data['name'])
            topic.save()
        else:
            topic = self.topic

        post = Post(
            topic=topic, user=self.user, user_ip=self.ip,
            #markup=self.cleaned_data['markup'],
            body=self.cleaned_data['body']
        )
        post.save()
        return post


class EditProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        """
        fields = ['site', 'jabber', 'icq', 'msn', 'aim', 'yahoo',
                  'location', 'signature', 'time_zone', 'language',
                  'avatar', 'show_signatures',
                  'markup',
                  ]
        """
        fields = ['site', 'jabber', 'icq', 'msn', 'aim', 'yahoo',
                  'location', 'signature', 'time_zone', 'language',
                  'show_signatures',
                  'markup',
                  ]

    #def __init__(self, *args, **kwargs):
        #super(EditProfileForm, self).__init__(*args, **kwargs)

    def clean_signature(self):
        value = self.cleaned_data['signature'].strip()
        if len(re.findall(r'\n', value)) > pybb_settings.SIGNATURE_MAX_LINES:
            raise forms.ValidationError('Number of lines is limited to %d' % pybb_settings.SIGNATURE_MAX_LINES)
        if len(value) > pybb_settings.SIGNATURE_MAX_LENGTH:
            raise forms.ValidationError('Length of signature is limited to %d' % pybb_settings.SIGNATURE_MAX_LENGTH)
        return value

class EditPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            #'markup',
            'body'
        ]

    def save(self):
        post = super(EditPostForm, self).save(commit=False)
        post.updated = datetime.now()
        post.save()
        return post


class UserSearchForm(forms.Form):
    query = forms.CharField(required=False, label='')

    def filter(self, qs):
        if self.is_valid():
            query = self.cleaned_data['query']
            return qs.filter(username__contains=query)
        else:
            return qs


class CreatePMForm(forms.ModelForm):
    recipient = forms.CharField(label=_('Recipient'))

    class Meta:
        model = PrivateMessage
        fields = ['subject', 'body', 'markup']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreatePMForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['recipient', 'subject', 'body', 'markup']

    def clean_recipient(self):
        name = self.cleaned_data['recipient']
        try:
            user = User.objects.get(nickname__iexact=name)
        except User.DoesNotExist:
            raise forms.ValidationError(_('User with login %s does not exist') % name)
        else:
            return user

    def save(self):
        pm = PrivateMessage(src_user=self.user, dst_user=self.cleaned_data['recipient'])
        pm = forms.save_instance(self, pm)
        return pm


class AddPollForm(forms.ModelForm):
    """form which operates with add ``Poll`` instance action"""
    items_amount = forms.IntegerField(
        label=_("Poll items amount"),
        help_text=_("poll items amount for voting"),
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Poll
        fields = ('title', 'items_amount', 'is_multiple', 'date_expire', )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'date_expire': forms.TextInput(
                attrs={
                    'class': 'datetimepicker form-control',
                    'data-format': 'YYYY-MM-DD HH:mm'
                }
            )
        }

    class Media:
        js = (
            '/media/components/moment/min/moment.min.js',
            '/media/components/eonasdan-bootstrap-datetimepicker/build/js/'
                'bootstrap-datetimepicker.min.js',
            '/media/components/eonasdan-bootstrap-datetimepicker/src/js/'
                'locales/bootstrap-datetimepicker.ru.js',
            '/media/js/datetimepickers.js'
        )


class UpdatePollForm(forms.ModelForm):
    """form which operates with update ``Poll`` instance action"""
    def clean_items_amount(self):
        items_amount = self.cleaned_data['items_amount']
        if self.instance.items_amount > items_amount:
            raise forms.ValidationError(
                _(
                    "You can not set items amount less than"
                    "the variants to select"
                )
            )
        return items_amount

    class Meta:
        model = Poll
        fields = ('title', 'items_amount', )
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'items_amount': forms.NumberInput(attrs={'class': 'form-control'})
        }


class AgreeForm(forms.Form):
    agree = forms.BooleanField(label=_("Agree"),
                               help_text=_("Yes, I agree"), required=True)


class PollItemForm(forms.ModelForm):
    """common ``PollItem`` instance actions form (create, update)"""
    title = forms.CharField(
        label=_("Poll item title"),
        help_text=_("poll item title users would vote on"), required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = PollItem
        fields = ('title', )


class PollItemBaseinlineFormset(BaseInlineFormSet):
    """ formset for operations with ``Poll``->``PollItem``
    instances."""
    def clean(self):
        super(PollItemBaseinlineFormset, self).clean()
        for form in self.forms:
            if form.is_valid():
                if not len(form.cleaned_data.keys()):
                    msg = _("Title should be set")
                    form._errors['title'] = ErrorList([msg])
        return self.cleaned_data if hasattr(self, 'cleaned_data') else []


class PollVoteFormMixin(object):
    def __init__(self, *args, **kwargs):
        if not 'poll' in kwargs:
            raise ImproperlyConfigured(
                "PollForm should always initialized with Poll instance"
            )
        self.poll = kwargs.pop('poll')
        if not self.poll or not isinstance(self.poll, Poll):
            raise ImproperlyConfigured("poll should be Poll instance")
        super(PollVoteFormMixin, self).__init__(*args, **kwargs)


class SingleVotePollForm(PollVoteFormMixin, forms.ModelForm):
    vote = forms.ModelChoiceField(
        label=_("Your option"), widget=forms.RadioSelect,
        queryset=PollItem.objects, empty_label=None
    )

    def __init__(self, *args, **kwargs):
        super(SingleVotePollForm, self).__init__(*args, **kwargs)
        self.fields['vote'].queryset = self.poll.items.all()

    class Meta:
        model = PollAnswer
        fields = ()


class MultipleVotePollForm(PollVoteFormMixin, forms.ModelForm):
    vote = forms.ModelMultipleChoiceField(
        label=_("Your option"), widget=forms.CheckboxSelectMultiple,
        queryset=PollItem.objects
    )

    def __init__(self, *args, **kwargs):
        super(MultipleVotePollForm, self).__init__(*args, **kwargs)
        self.fields['vote'].queryset = self.poll.items.all()

    class Meta:
        model = PollAnswer
        fields = ()