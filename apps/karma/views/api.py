# coding: utf-8
import django_filters
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import exceptions
from apps.karma.serializers import (
    KarmaSerializer,
)
from apps.karma.models import Karma

__all__ = ['KarmaViewSet', ]


class KarmaFilterSet(django_filters.FilterSet):
    class Meta:
        model = Karma


class KarmaPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # GET, HEAD, OPTION is allowed for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        privileged = request.user and request.user.is_authenticated()
        return privileged

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        # priveleged users has all access,
        # owners can not cast DELETE method (forbidden ones)
        privileged = request.user and request.user.has_perm(
            'karma.change_karma')
        forbidden_user_methods = ['DELETE', 'PUT']
        if request.user == obj.voter:
            return request.method not in forbidden_user_methods
        return privileged


class KarmaViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for Karma instance
    """
    queryset = Karma.objects.all()
    serializer_class = KarmaSerializer
    filter_class = KarmaFilterSet
    permission_classes = (KarmaPermission, )
