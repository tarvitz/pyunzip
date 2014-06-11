# coding: utf-8
import django_filters
from apps.tabletop.models import Codex, Roster
from rest_framework import viewsets
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

    def get_queryset(self):
        qs = super(RosterViewSet, self).get_queryset()
        if self.request.user.is_authenticated():
            return qs.filter(owner=self.request.user)
        return Roster.objects.none()


class CodexViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for codex
    """
    queryset = Codex.objects.all()
    serializer_class = CodexSerializer
    filter_class = CodexFilterSet
