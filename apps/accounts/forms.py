# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from apps.accounts.models import User
from django.contrib import auth


#mixins
class CleanPasswordMixin(object):
    def clean(self):
        cd = super(CleanPasswordMixin, self).clean()
        password = cd.get('password')
        password2 = cd.get('password2')
        if all((password, password2)):
            if password != password2:
                msg = _("Passwords does not match")
                self._errors['password'] = ErrorList([msg])
                if 'password' in cd:
                    cd.pop('password')
                if 'password2' in cd:
                    cd.pop('password2')
        return cd


class LoginForm(forms.Form):
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput)

    def clean(self):
        cd = self.cleaned_data
        username = cd.get('username')
        password = cd.get('password')

        user = auth.authenticate(username=username, password=password)
        if not user:
            # fail to authenticate, probabbly incorrect auth data
            msg = _("Sorry your username or/and password are invalid")
            self._errors['password'] = ErrorList([msg])
            if 'password' in cd:
                del cd['password']
        
        cd['user'] = user
        return cd


class AgreeForm(forms.Form):
    agree = forms.BooleanField(
        label=_("Yes, I agree"),
        required=True
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', )