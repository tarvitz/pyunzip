# coding: utf-8
import django_filters
from apps.wh.models import (
    Universe, Fraction, Side, Army, Rank, RankType, MiniQuote, Expression)

from rest_framework import viewsets
from rest_framework import permissions
from apps.wh.serializers import *

__all__ = ['UniverseViewSet', 'FractionViewSet', 'SideViewSet',
           'ArmyViewSet', 'RankViewSet', 'RankTypeViewSet', 'MiniQuoteViewSet',
           'ExpressionViewSet']


class UniverseViewSet(viewsets.ModelViewSet):
    queryset = Universe.objects.all()
    serializer_class = UniverseSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class FractionViewSet(viewsets.ModelViewSet):
    queryset = Fraction.objects.all()
    serializer_class = FractionSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class SideViewSet(viewsets.ModelViewSet):
    queryset = Side.objects.all()
    serializer_class = SideSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class ArmyViewSet(viewsets.ModelViewSet):
    queryset = Army.objects.all()
    serializer_class = ArmySerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class RankViewSet(viewsets.ModelViewSet):
    queryset = Rank.objects.all()
    serializer_class = RankSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class RankTypeViewSet(viewsets.ModelViewSet):
    queryset = RankType.objects.all()
    serializer_class = RankTypeSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class MiniQuoteViewSet(viewsets.ModelViewSet):
    queryset = MiniQuote.objects.all()
    serializer_class = MiniQuoteSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class ExpressionViewSet(viewsets.ModelViewSet):
    queryset = Expression.objects.all()
    serializer_class = ExpressionSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )