# coding: utf-8

import django_filters
from apps.core.rest import IsOwnerOrReadOnly
from apps.tabletop.models import Codex, Roster

from rest_framework import viewsets
from rest_framework import permissions
from apps.tabletop.serializers import CodexSerializer, RosterSerializer


class CodexFilterSet(django_filters.FilterSet):
    class Meta:
        model = Codex


class RosterFilterSet(django_filters.FilterSet):
    class Meta:
        model = Roster


class RosterViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for roster
    """
    queryset = Roster.objects.all()
    serializer_class = RosterSerializer
    filter_class = RosterFilterSet
    permission_classes = (permissions.IsAuthenticated,
                          IsOwnerOrReadOnly, )

    def check_object_permissions(self, request, obj):
        # privileged users have whole access
        if request.user.has_perm('tabletop.change_roster'):
            return True
        return super(RosterViewSet, self).check_object_permissions(
            request, obj)


class CodexPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.has_perm('tabletop.change_codex')


class CodexViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for codex
    """
    queryset = Codex.objects.all()
    serializer_class = CodexSerializer
    filter_class = CodexFilterSet
    permission_classes = (CodexPermission, )
