# -*- coding: utf-8 -*-
from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _
from apps.accounts.models import (
    User, AccountRequest, AccountRequestee, Spec
)
from apps.core.forms import RequestMixin
from apps.core.helpers import get_object_or_None
from django.forms.formsets import formset_factory
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured


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


class AccountRequestForm(CleanPasswordMixin, forms.ModelForm):
    required_css_class = 'required'
    password = forms.CharField(
        label=_("Password"), help_text=_("Your password"),
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label=_("Password repeat"),
        help_text=_("Please repeat your password"),
        widget=forms.PasswordInput
    )
    company_title = forms.CharField(
        label=_("Company title"), required=False
    )

    def clean_email(self):
        email = self.cleaned_data['email']
        user_request = get_object_or_None(
            AccountRequest, email__iexact=email
        )
        user_exist = get_object_or_None(
            User, email__iexact=email)

        if any((user_request, user_exist)):
            raise forms.ValidationError(_("This email is already registered"))
        return email

    def save(self, commit=True):
        self.instance.set_password(self.cleaned_data['password'])
        return super(AccountRequestForm, self).save(commit)

    class Meta:
        model = AccountRequest
        # wizard
        fields = (
            'email', 'real_name', 'company_title',
        )


class AccountRequesteeForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = AccountRequestee
        fields = ('full_name', 'email', 'course')
        widgets = {
            'full_name': forms.TextInput(
                attrs={
                    'placeholder': _("Full name of participant"),
                }
            ),
            'email': forms.TextInput(
                attrs={
                    'placeholder': _("jonhrambo@company.com")
                }
            )
        }

AccountRequesteeFormset = formset_factory(AccountRequesteeForm, extra=1,
                                          max_num=10)


class AccountRequestUpdateForm(RequestMixin, forms.ModelForm):
    required_css_class = 'required'

    def __init__(self, *args, **kwargs):
        super(AccountRequestUpdateForm, self).__init__(*args, **kwargs)
        user = self.request.user
        if not any((user.is_admin, user.is_auditor)):
            if user.is_secretary:
                self.fields.pop('cost')
            else:
                # permission should be denied before this run
                raise ImproperlyConfigured(
                    "Only admin, secretary and auditor"
                    "have an access to this block"
                )

    class Meta:
        model = AccountRequest
        fields = (
            'email', 'real_name', 'company_title',
            'is_user_created'
        )


class AgreeForm(forms.Form):
    agree = forms.BooleanField(
        label=_("Yes, I agree"),
        required=True
    )


class AddRoleForm(CleanPasswordMixin, forms.ModelForm):
    """
    uses for create and update views
    """
    required_css_class = 'required'
    email = forms.EmailField(
        label=_("Email"), required=True
    )
    password = forms.CharField(
        label=_("Password")
    )
    password2 = forms.CharField(
        label=_("Password repeat")
    )
    specs = forms.ModelMultipleChoiceField(
        queryset=Spec.objects, label=_("Specializations"),
        help_text=_("Please select teacher specializations"),
        widget=forms.SelectMultiple(
            attrs={'class': 'chosen'}
        ), required=False
    )

    def save(self, commit=True):
        self.instance.set_password(self.cleaned_data['password'])
        self.instance.is_teacher = True
        return super(AddRoleForm, self).save(commit)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'specs', 'is_operator')


class UpdateRoleForm(forms.ModelForm):
    specs = forms.ModelMultipleChoiceField(
        queryset=Spec.objects, label=_("Specializations"),
        help_text=_("Please select teacher specializations"),
        widget=forms.SelectMultiple(
            attrs={'class': 'chosen'}
        ), required=False
    )

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'specs',
            'is_operator', 'is_teacher'
        )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'is_subscribed')