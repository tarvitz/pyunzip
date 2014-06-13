import warnings

warnings.warn(
    "django-tastypie dependency is deprecated as well as any code with its "
    "usage. It would be deleted in near future.",
    PendingDeprecationWarning)

from apps.accounts.models import User
from django.utils.translation import ugettext_lazy as _
from tastypie.resources import ModelResource
from tastypie.authorization import DjangoAuthorization
from tastypie.validation import FormValidation
from tastypie.exceptions import Unauthorized
from tastypie.authentication import (
    MultiAuthentication, BasicAuthentication,
    ApiKeyAuthentication
)
from django import forms


class UserForm(forms.ModelForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            return email
        exists = User.objects.filter(email__iexact=email).count()
        if exists:
            raise forms.ValidationError(_("User with such email exists"))
        return email

    class Meta:
        model = User
        fields = ('username', 'email')


class SuperUserOnlyAuth(DjangoAuthorization):
    def read_list(self, object_list, bundle):
        if not bundle.request.user.is_superuser:
            raise Unauthorized("Insufficient level access")
        return object_list

    def read_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        return bundle.request.user.is_superuser

    def create_list(self, object_list, bundle):
        # Assuming their auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        return bundle.request.user.is_superuser

    def update_list(self, object_list, bundle):
        if not bundle.request.user.is_superuser:
            raise Unauthorized("Insufficient level access")
        return object_list

    def update_detail(self, object_list, bundle):
        return bundle.request.user.is_superuser

    def delete_list(self, object_list, bundle):
        # Sorry user, no deletes for you!
        raise Unauthorized("No delete operations allowed")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("No delete operations allowed.")


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authorization = SuperUserOnlyAuth()
        authentication = MultiAuthentication(
            BasicAuthentication(),
            ApiKeyAuthentication()
        )
        validation = FormValidation(form_class=UserForm)
        excludes = ['password', ]