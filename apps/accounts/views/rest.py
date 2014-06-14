# coding: utf-8
import django_filters
from apps.accounts.models import User
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from apps.accounts.serializers import UserSerializer


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