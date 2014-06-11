# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()


class SuperUserLoginForm(forms.ModelForm):
    username = forms.CharField(label=_('username'))

    class Meta:
        model = User
        fields = []
