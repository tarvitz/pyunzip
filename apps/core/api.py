# coding: utf-8
from django.core.exceptions import ImproperlyConfigured
from rest_framework import permissions


class IsOwnerOrModelAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to allow admins to object modifications.
    Allow access object owners to instances.
    """
    _permission_format = '%(app)s.%(prefix)s_%(model)s'
    owner_fields = ['user', 'owner']

    def get_owner_fields(self):
        return self.owner_fields

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        is_owner = False
        for owner_field in self.get_owner_fields():
            if hasattr(obj, owner_field):
                is_owner = getattr(obj, owner_field) == request.user

        if is_owner:
            return is_owner

        if request.method == 'POST':
            prefix = 'add'
        elif request.method in ('PUT', 'PATCH'):
            prefix = 'change'
        elif request.method == 'DELETE':
            prefix = 'delete'
        else:
            prefix = 'change'

        app = obj._meta.app_label
        model_name = obj._meta.model_name

        perm = self._permission_format % {
            'app': app,
            'model': model_name,
            'prefix': prefix
        }
        return request.user and request.user.has_perm(perm)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        else:
            raise ImproperlyConfigured(
                "Model has no `owner` or `user` "
                "fields to compare them agains request.user."
            )


class IsModelAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to allow admins to object modifications.
    """
    _permission_format = '%(app)s.%(prefix)s_%(model)s'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        model = view.queryset.model
        app = model._meta.app_label
        model_name = model._meta.model_name
        perm = self._permission_format % {
            'app': app,
            'model': model_name,
            'prefix': 'add'
        }
        return request.user and request.user.has_perm(perm)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            prefix = 'add'
        elif request.method in ('PUT', 'PATCH'):
            prefix = 'change'
        elif request.method == 'DELETE':
            prefix = 'delete'
        else:
            prefix = 'change'

        app = obj._meta.model.app_label
        model_name = obj._meta.model.model_name

        perm = self._permission_format % {
            'app': app,
            'model': model_name,
            'prefix': prefix
        }
        return request.user and request.user.has_perm(perm)