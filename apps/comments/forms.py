# coding: utf-8
from apps.comments.models import CommentWatch
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.comments.models import Comment


class CommentWatchSubscribeForm(forms.ModelForm):
    required_css_class = 'required'
    agree = forms.BooleanField(label=_("Yes, I agree"), required=True,)
    content_type = forms.ModelChoiceField(queryset=ContentType.objects,
                                          widget=forms.HiddenInput)
    object_pk = forms.IntegerField(min_value=1, widget=forms.HiddenInput)

    class Meta:
        model = CommentWatch
        fields = ('agree', 'content_type', 'object_pk', )


class CommentForm(forms.ModelForm):
    content_type = forms.ModelChoiceField(queryset=ContentType.objects,
                                          widget=forms.HiddenInput)
    object_pk = forms.IntegerField(min_value=1, widget=forms.HiddenInput)
    syntax = forms.ChoiceField(choices=settings.SYNTAX,
                               widget=forms.HiddenInput)
    url = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ('comment', 'content_type', 'object_pk', 'syntax', )
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'markitup'})
        }


class SubscriptionRemoveForm(forms.ModelForm):
    agree = forms.BooleanField(label=_("Yes, I agree"), required=True)

    class Meta:
        model = CommentWatch
        fields = ()