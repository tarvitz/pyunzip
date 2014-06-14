# coding: utf-8
import django_filters
from apps.accounts.models import User, PM, PolicyWarning
from rest_framework import viewsets
from rest_framework import permissions
from django.db.models import Q
from apps.accounts.serializers import (
    UserSerializer, PMSerializer, PolicyWarningSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_superuser


class UserFilterSet(django_filters.FilterSet):
    class Meta:
        model = User


class UserViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for event
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrReadOnly, )
    # filter_class = UserSerializer

    def get_queryset(self):
        qs = super(UserViewSet, self).get_queryset()
        if self.request.user.is_authenticated():

            return (
                qs if self.request.user.has_perm('accounts.change_user')
                else qs.filter(pk=self.request.user.pk)
            )
        return qs.none()


class PMPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        privileged = request.user and request.user.has_perm(
            'accounts.change_pm')
        if privileged:
            return True
        if request.method in ('PATCH', 'PUT', 'DELETE'):
            return False
        return True

    def has_object_permission(self, request, view, obj):
        """ only sender, addressee can watch their private messages

        :param request:
        :param view:
        :param obj:
        :return:
        """
        if request.user not in (obj.sender, obj.addressee):
            return False
        return True


class PMViewSet(viewsets.ModelViewSet):
    queryset = PM.objects.all()
    serializer_class = PMSerializer
    permission_classes = (permissions.IsAuthenticated, PMPermission)

    def get_queryset(self):
        qs = super(PMViewSet, self).get_queryset()
        qset = Q(sender=self.request.user) | Q(addressee=self.request.user)
        privileged = self.request.user.has_perm('accounts.change_pm')
        return qs if privileged else qs.filter(qset)


class PolicyWarningPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return (
                request.user and
                request.user.has_perm('accounts.change_policywarning')
            )
        return True

    def has_object_permission(self, request, view, obj):
        privileged = (
            request.user and
            request.user.has_perm('accounts.change_policywarning')
        )
        if privileged:
            return True
        if (request.method in permissions.SAFE_METHODS
                and request.user == obj.user):
            return True
        return False


class PolicyWarningViewSet(viewsets.ModelViewSet):
    queryset = PolicyWarning.objects.all()
    serializer_class = PolicyWarningSerializer
    permission_classes = (permissions.IsAuthenticated,
                          PolicyWarningPermission, )

    def get_queryset(self):
        qs = super(PolicyWarningViewSet, self).get_queryset()
        privileged = self.request.user.has_perm(
            'accounts.change_policywarning')
        return qs if privileged else qs.filter(user=self.request.user)