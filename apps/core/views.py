# coding: utf-8
import os
from django.http import (
    HttpResponse, )
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.shortcuts import redirect

import logging
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.generic import detail

logger = logging.getLogger(__name__)


def robots(request):
    response = HttpResponse()
    response['Content-Type'] = 'text/plain'
    content = open(os.path.join(settings.MEDIA_ROOT, 'robots.txt'), 'r').read()
    response.write(content)
    return response


def index(request):
    return redirect(reverse('pybb:index'))


def safe_url(request):
    return redirect(request.GET.get('url', '/'))


# CBV Mixins
# noinspection PyUnresolvedReferences
class RequestMixin(object):
    def get_form_kwargs(self):
        kwargs = super(RequestMixin, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs


# noinspection PyUnresolvedReferences
class LoginRequiredMixin(object):
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs
        )


# noinspection PyUnresolvedReferences
class TemplateNamesMixin(object):
    # noinspection PyProtectedMember
    def get_template_names(self):
        """
        :return: list of template names formatted within '_'
        symbols between class words, e.g.
        TestItem binds as test_item
        TestItemStuff binds as test_item_stuff
        """

        if self.template_name:
            return self.template_name

        name = self.model._meta.object_name
        app_label = self.model._meta.app_label
        name = (
            name[0].lower() + "".join(
                ['_' + i if i.isupper() else i for i in name[1:]]
            ).lower()
        )
        template_name = "{app}/{model}{suffix}.html".format(
            app=app_label,
            model=name,
            suffix=self.template_name_suffix or ''
        )

        return [template_name, ]


class BasePermission(object):
    def has_permission(self, request):
        return True

    def has_object_permission(self, request, obj):
        return True


class PermissionMixin(BasePermission):
    """
    check for permissions
    """
    def dispatch(self, request, *args, **kwargs):
        allowed = self.has_permission(request)
        allowed = (
            allowed and
            self.has_object_permission(request, self.get_object())
        )
        if not allowed:
            raise PermissionDenied("permission denied")
        return super(PermissionMixin, self).dispatch(request, *args, **kwargs)


class GenericModelAccessMixin(BasePermission, detail.SingleObjectMixin):
    permission_prefix = None

    def has_permission(self, request):
        if not hasattr(self, "model"):
            raise ImproperlyConfigured("no `model` passed")
        permission = '%(app)s.%(prefix)s_%(model)s'

        if isinstance(self, generic.CreateView):
            prefix = 'add'
        elif isinstance(self, generic.UpdateView):
            prefix = 'change'
        elif isinstance(self, generic.DeleteView):
            prefix = 'delete'
        else:
            prefix = self.permission_prefix

        if prefix is None:
            raise ImproperlyConfigured(
                "permission prefix should be set for FormView, "
                "TemplateView and the other views by user"
            )
        permission = permission % {
            'app': self.model._meta.app_label,
            'model': self.model._meta.model_name,
            'prefix': prefix
        }
        return request.user and request.user.has_perm(permission)


class OwnerModelOrAdminAccessMixin(PermissionMixin, detail.SingleObjectMixin):
    owner_field = 'owner'
    permission_prefix = 'change'
    _permission = '%(app)s.%(prefix)s_%(model)s'

    def has_object_permission(self, request, obj):
        if not hasattr(obj, self.owner_field):
            raise ImproperlyConfigured(
                "owner_field which is set to `%s` does not exist in "
                "`%s` instance" % (self.owner_field, self.model.__repr__())
            )
        if isinstance(self, generic.UpdateView):
            prefix = 'change'
        elif isinstance(self, generic.DeleteView):
            prefix = 'delete'
        else:
            prefix = self.permission_prefix
        permission = self._permission % {
            'app': self.model._meta.app_label,
            'model': self.model._meta.model_name,
            'prefix': prefix
        }
        return (
            getattr(obj, self.owner_field) == request.user
            or request.user.has_perm(permission)
        )
