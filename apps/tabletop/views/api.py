# coding: utf-8

import django_filters
from apps.core.api import IsOwnerOrModelAdminOrReadOnly, IsOwnerOrReadOnly
from apps.tabletop.models import Codex, Roster, Report, Mission, Game

from rest_framework import viewsets
from rest_framework import permissions
from apps.tabletop.serializers import (
    CodexSerializer, MissionSerializer, GameSerializer, ReportSerializer,
    RosterSerializer
)


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


class CodexViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for codex
    """
    queryset = Codex.objects.all()
    serializer_class = CodexSerializer
    filter_class = CodexFilterSet
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = (IsOwnerOrModelAdminOrReadOnly, )


class MissionViewSet(viewsets.ModelViewSet):
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.all()
    serializer_class = GameSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
