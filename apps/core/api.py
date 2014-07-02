# coding: utf-8
from django.core.exceptions import ImproperlyConfigured
from rest_framework import permissions


class AdminModelPermissionMixin(object):
    _permission_format = '%(app)s.%(prefix)s_%(model)s'

    def get_admin_model_permission(self, request, view):
        if request.method == 'POST':
            prefix = 'add'
        elif request.method in ('PUT', 'PATCH'):
            prefix = 'change'
        elif request.method == 'DELETE':
            prefix = 'delete'
        else:
            prefix = 'change'
        app = view.queryset.model._meta.app_label
        model = view.queryset.model._meta.model_name
        perm = self._permission_format % {
            'app': app,
            'model': model,
            'prefix': prefix
        }
        return perm


class IsOwnerOrModelAdminOrReadOnly(AdminModelPermissionMixin,
                                    permissions.BasePermission):
    """
    Object-level permission to allow admins to object modifications.
    Allow access object owners to instances.
    """
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

        perm = self.get_admin_model_permission(request, view)
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


class IsModelAdminOrReadOnly(AdminModelPermissionMixin,
                             permissions.BasePermission):
    """
    Object-level permission to allow admins to object modifications.
    """
    _permission_format = '%(app)s.%(prefix)s_%(model)s'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        perm = self.get_admin_model_permission(request, view)
        return request.user and request.user.has_perm(perm)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        perm = self.get_admin_model_permission(request, view)
        return request.user and request.user.has_perm(perm)


class IsOwnerOrModelAdminOrPermissionDenied(permissions.BasePermission):
    pass