# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from cStringIO import StringIO
from PIL import Image
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from apps.wh.models import Side, Army, PM
from apps.core.models import UserSID
from apps.core.helpers import get_object_or_None
from apps.core.forms import (
    RequestModelForm, RequestForm,
    RequestFormMixin
)
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.contrib import auth
import re


class WarningForm(RequestFormMixin, forms.Form):
    nickname = forms.CharField(widget=forms.HiddenInput())
    level = forms.ChoiceField(choices=settings.SIGN_CHOICES, required=False)
    comment = forms.CharField(
        required=False, widget=forms.Textarea({'cols': 40, 'rows': 10})
    )
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    
    def clean_level(self):
        level = int(self.cleaned_data.get('level', 1))
        if level > len(settings.SIGN_CHOICES) or level <= 0:
            raise forms.ValidationError(
                _('Level should not be greater than %i' % (
                    len(settings.SIGN_CHOICES)))
            )
        return level


class UploadAvatarForm(forms.Form):
    avatar = forms.ImageField()

    def clean_avatar(self):
        value = self.cleaned_data.get('avatar', '')
        bulk = ''
        for i in value.chunks():
            bulk += i
        content = bulk
        if 'content-type' in value:
            main, sub = value['content-type'].split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png', 'jpg']):
                raise forms.ValidationError(
                    _('jpeg, png, gif, jpg image only')
                )
        try:
            img = Image.open(StringIO(content))
            x, y = img.size
        except:
            raise forms.ValidationError(
                _(
                    'Upload a valid avatar. The file you uploaded '
                    'was either not an image or a corrupted image.'
                )
            )
        if y > 100 or x > 100:
            raise forms.ValidationError(
                _(
                    'Upload a valid avatar. Avatar\'s size should '
                    'not be greater than 100x100 pixels'
                )
            )
        return value


class UpdateProfileModelForm(RequestFormMixin, forms.ModelForm):
    required_css_class = 'required'
    first_name = forms.CharField(
        label=_("Name"), widget=forms.TextInput(
            attrs={'class': 'form-control'}
        )
    )
    side = forms.ModelChoiceField(
        queryset=Side.objects, required=False,
        widget=forms.Select(
            attrs={'class': 'form-control', 'data-class': 'chosen'})
    )
    army = forms.ModelChoiceField(
        queryset=Army.objects.none(), required=True,
        widget=forms.Select(
            attrs={'class': 'form-control', 'data-class': 'chosen'})
    )

    def __init__(self, *args, **kwargs):
        super(UpdateProfileModelForm, self).__init__(*args, **kwargs)
        user = self.request.user
        if all(self.data or [None, ]):
            self.fields['army'].queryset = Army.objects.all()
        else:
            if user.army:
                self.fields['army'].queryset = Army.objects.filter(
                    side__pk=user.army.side.pk
                )
                self.fields['side'].initial = user.army.side
                self.fields['army'].initial = user.army

    def clean_nickname(self):
        current_nickname = self.request.user.nickname
        nick = self.cleaned_data.get('nickname', '')
        r = re.compile(r'[\w\s-]+', re.U)
        if not r.match(nick):
            raise forms.ValidationError(
                _('You can not use additional symbols in you nickname')
            )
        user = get_object_or_None(
            User, nickname__exact=nick,
        )
        if not user:
            return nick

        user_nickname = (
            getattr(user, 'nickname')
            if hasattr(user, 'nickname') else None
        )
        if not user_nickname == current_nickname and user != self.request.user:
            raise forms.ValidationError(
                _('Another user with %s nickname exists.' % nick)
            )
        return nick

    def clean_avatar(self):
        value = self.cleaned_data.get('avatar', '')
        if not value:
            return None
        bulk = ''
        for i in value.chunks():
            bulk += i
        content = bulk

        if 'content-type' in value:
            main, sub = value['content-type'].split('/')
            if not (main == 'image' and sub in ['jpeg', 'gif', 'png', 'jpg']):
                raise forms.ValidationError(
                    _('jpeg, png, gif, jpg image only'))
        try:
            img = Image.open(StringIO(content))
            x, y = img.size
        except:
            raise forms.ValidationError(_(
                'Upload a valid avatar. The file you uploaded was either'
                'not an image or a corrupted image.'
            ))
        if y > 100 or x > 100:
            raise forms.ValidationError(_(
                'Upload a valid avatar. Avatar\'s size should not be '
                'greater than 100x100 pixels'
            ))
        return value

    def clean_jid(self):
        jid = self.cleaned_data['jid']
        if jid:
            from apps.core.helpers import get_object_or_None
            u = self.request.user
            user = get_object_or_None(User, jid__iexact=jid)
            if user and user != u:
                raise forms.ValidationError(
                    _('User with such JID already exists'))
        return "".join(jid).lower()

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'nickname', 'avatar',
            'gender', 'jid', 'uin', 'about', 'side', 'army', 'tz'
        ]
        exclude = [
            'password', 'username', 'groups', 'ranks', 'user_permissions',
            'is_staff', 'is_superuser', 'is_active', 'last_login',
            'date_joined', 'plain_avatar',
        ]

        widgets = {
            'last_name': forms.TextInput(
                attrs={'class': 'form-control'}),
            'email': forms.TextInput(
                attrs={'class': 'form-control'}),
            'nickname': forms.TextInput(
                attrs={'class': 'form-control'}),
            'gender': forms.Select(
                attrs={'class': 'form-control', 'data-class': 'chosen'}),
            'jid': forms.TextInput(
                attrs={'class': 'form-control'}),
            'uin': forms.TextInput(
                attrs={'class': 'form-control'}),
            'about': forms.TextInput(
                attrs={'class': 'form-control'}),
            'skin': forms.Select(
                attrs={'class': 'form-control', 'data-class': 'chosen'}),
            'first_name': forms.Select(
                attrs={'class': 'form-control', 'data-class': 'chosen'}),
            'tz': forms.Select(
                attrs={'class': 'form-control', 'data-class': 'chosen'}),

        }


class PMForm(RequestModelForm):
    addressee = forms.ModelChoiceField(
        label=_("Addressee"),
        widget=forms.Select(attrs={
            'class': 'ajax-chosen form-control',
            'url': reverse('json:wh:users')
        }),
        queryset=User.objects.none()
    )
    content = forms.CharField(
        label=_("Content"),
        widget=forms.Textarea(attrs={'class': 'markitup form-control'})
    )

    def __init__(self, *args, **kwargs):
        super(PMForm, self).__init__(*args, **kwargs)
        if all(self.data or [None, ]):
            self.base_fields['addressee'].queryset = User.objects
            self.fields['addressee'].queryset = User.objects
        else:
            self.base_fields['addressee'].queryset = User.objects.none()
            self.fields['addressee'].queryset = User.objects.none()

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


class RecoverForm(forms.Form):
    email = forms.EmailField()
    

class AddWishForm(forms.Form):
    post = forms.CharField(widget=forms.Textarea())


class PasswordChangeForm(RequestForm):
    old_password = forms.CharField(widget=forms.PasswordInput())
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

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


class PasswordRecoverForm(RequestForm):
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


class SuperUserLoginForm(forms.ModelForm):
    username = forms.CharField(label=_('username'))

    class Meta:
        model = User
        fields = []


class LoginForm(forms.ModelForm):
    password = forms.CharField(
        label=_('password'), widget=forms.PasswordInput(
            attrs={'class': 'form-control'}
        ),
        required=True
    )
    next = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if all((username, password)):
            user = auth.authenticate(username=username, password=password)
            if not user:
                msg = _("No user or password match")
                self._errors['username'] = ErrorList([msg])
            else:
                self.cleaned_data['user'] = user
                if not user.is_active:
                    msg = _("You have been banned ;)")
                    self._errors['username'] = ErrorList([msg])
        return self.cleaned_data

    class Meta:
        model = User
        fields = ['username', 'password']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'})
        }


class PasswordRestoreInitiateForm(forms.Form):
    email = forms.CharField(
        label=_("Email"), help_text=_("Your email")
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


class PasswordRestoreForm(RequestModelForm):
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