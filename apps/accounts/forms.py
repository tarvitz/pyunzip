# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from apps.accounts.models import User
from django.contrib import auth

from captcha.fields import ReCaptchaField


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
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))

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


class RegisterForm(forms.ModelForm):
    required_css_class = 'required'
    username = forms.CharField(
        label=_("Username"), required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_repeat = forms.CharField(
        label=_("Password repeat"),
        widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    nickname = forms.CharField(
        label=_("Nickname"),
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    captcha = ReCaptchaField(
        label=_("Captcha")
    )

    class Meta:
        model = User
        fields = ('username', 'nickname', 'email', )
        widgets = {
        }
        exclude = ('password', )