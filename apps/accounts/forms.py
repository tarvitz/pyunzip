# -*- coding: utf-8 -*-
from apps.accounts.models import User, PM, PolicyWarning
from apps.core.forms import RequestFormMixin
from apps.core.helpers import get_object_or_None
from apps.core.widgets import DatePickerInput
from apps.core.models import UserSID

from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

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


class ProfileForm(RequestFormMixin, forms.ModelForm):
    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        exists = User.objects.filter(nickname__iexact=nickname).exclude(
            pk=self.request.user.pk)
        if exists.count():
            raise forms.ValidationError(
                _("Another user with user nickname exists."))
        return nickname

    class Meta:
        attrs = {'class': 'form-control'}
        model = User
        fields = ('first_name', 'last_name', 'nickname', 'avatar', 'army',
                  'gender',
                  'jid',
                  'about')
        widgets = {
            'first_name': forms.TextInput(attrs),
            'last_name': forms.TextInput(attrs),
            'nickname': forms.TextInput(attrs),
            'gender': forms.Select(attrs),
            'jid': forms.EmailInput(attrs),
            'about': forms.TextInput(attrs),
            'army': forms.Select(
                attrs={'class': 'form-control', 'data-toggle': 'select2'})
        }


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

    def clean_nickname(self):
        nickname = self.cleaned_data['nickname']
        exists = User.objects.filter(nickname__iexact=nickname)
        if exists.count():
            raise forms.ValidationError(
                _("Another user with user nickname exists."))
        return nickname

    class Meta:
        model = User
        fields = ('username', 'nickname', 'email', )
        widgets = {
        }
        exclude = ('password', )


class PasswordChangeForm(RequestFormMixin, forms.ModelForm):
    required_css_class = 'required'
    attrs = {'class': 'form-control'}
    old_password = forms.CharField(widget=forms.PasswordInput(attrs=attrs))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs=attrs))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs=attrs))

    def clean(self):
        cleaned_data = self.cleaned_data
        old_password = cleaned_data.get('old_password', '')
        password1 = cleaned_data.get('password1', '')
        password2 = cleaned_data.get('password2', '')
        current_user = self.request.user
        if current_user.check_password(old_password):
            if password1 != password2:
                msg = _('Password1 and Password2 does not match')
                self._errors['password1'] = ErrorList([msg])
                if password1:
                    cleaned_data.pop('password1')
                if password2:
                    cleaned_data.pop('password2')
                if old_password:
                    cleaned_data.pop('old_password')
        else:
            msg = _(
                'Your current password does not match with one you\'ve input'
            )
            self._errors['old_password'] = ErrorList([msg])
            if old_password:
                cleaned_data.pop('old_password')
            if password1:
                cleaned_data.pop('password1')
            if password2:
                cleaned_data.pop('password2')
        return cleaned_data

    class Meta:
        attrs = {'class': 'form-control'}
        model = User
        fields = ()


class PasswordRecoverForm(RequestFormMixin, forms.ModelForm):
    email = forms.EmailField()
    login = forms.CharField()

    def clean(self):
        cleaned_data = self.cleaned_data
        email = self.cleaned_data.get('email', '')
        login = self.cleaned_data.get('login', '')

        user = get_object_or_None(User, username__iexact=login,
                                  email__iexact=email)
        if not user:
            msg = _('No such user with such email')
            self._errors['login'] = ErrorList([msg])
        return cleaned_data


class PasswordRestoreInitiateForm(forms.Form):
    email = forms.CharField(
        label=_("Email"), help_text=_("Your email"),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    def clean_email(self):
        email = self.cleaned_data['email'] or None
        users = User.objects.filter(email__iexact=email)
        if not users:
            raise forms.ValidationError(
                _("Users with given email does not exists")
            )
        self.cleaned_data['users'] = users
        return email


class PasswordRestoreForm(RequestFormMixin, forms.ModelForm):
    password = forms.CharField(
        label=_("Password"), widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label=_("Password repeat"), widget=forms.PasswordInput()
    )

    def clean(self):
        cd = self.cleaned_data
        password = cd['password']
        password2 = cd['password2']
        if all((password, password2) or (None, )):
            if password != password2:
                msg = _("Passwords don't match")
                self._errors['password'] = ErrorList([msg])
        return cd

    def save(self, commit=True):
        instance = self.instance
        user = self.instance.user
        user.set_password(self.cleaned_data['password'])
        user.save()
        if commit:
            instance.expired = True
            instance.save()
        else:
            instance.expired = True
            instance = super(PasswordRestoreForm, self).save(
                commit=commit)

        return instance

    class Meta:
        model = UserSID
        exclude = ('expired_date', 'expired', 'sid', 'user')


class PMReplyForm(RequestFormMixin, forms.ModelForm):
    class Meta:
        attrs = {'class': 'form-control'}
        model = PM
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'form-control markitup'}),
            'title': forms.TextInput(attrs=attrs)
        }
        fields = ('title', 'content')


class PMForm(RequestFormMixin, forms.ModelForm):
    required_css_class = 'required'
    addressee = forms.ModelChoiceField(
        label=_("Addressee"),
        queryset=User.objects,
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'data-toggle': 'select2'
            }
        ),
    )
    content = forms.CharField(
        label=_("Content"),
        widget=forms.Textarea(attrs={'class': 'markitup form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(PMForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = self.cleaned_data
        sender = self.request.user
        addressee = cleaned_data.get('addressee', '')
        try:
            a = User.objects.get(nickname=addressee)
            if sender == a:
                msg = _('You can not send private messages to yourself')
                self._errors['addressee'] = ErrorList([msg])
        except User.DoesNotExist:
            msg = _('There\'s no user with such nickname, sorry')
            self._errors['addressee'] = ErrorList([msg])
        return cleaned_data

    def save(self, commit=True):
        self.instance.sender = self.request.user
        self.instance.addressee = self.cleaned_data['addressee']
        return super(PMForm, self).save(commit)

    class Meta:
        model = PM
        fields = ('addressee', 'title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'})
        }


class PolicyWarningForm(forms.ModelForm):
    class Meta:
        attrs = {'class': 'form-control', 'klass': 'col-lg-2'}
        model = PolicyWarning
        widgets = {
            'user': forms.HiddenInput,
            'date_expired': DatePickerInput(attrs=attrs),
            'level': forms.Select(attrs=attrs),
            'comment': forms.Textarea(attrs={'class': 'form-control'})
        }
        fields = ('user', 'level', 'date_expired', 'comment', 'is_expired',)

    class Media:
        css = {
            'all': (
                'components/eonasdan-bootstrap-datetimepicker/build/css'
                '/bootstrap-datetimepicker.min.css',
            )
        }
        js = (
            'components/eonasdan-bootstrap-datetimepicker/build/js'
                '/bootstrap-datetimepicker.min.js',
            'js/datetimepickers.js'
        )