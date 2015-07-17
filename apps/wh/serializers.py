# coding: utf-8

from apps.wh.models import (
    Universe, Fraction, Side, Army, Rank, RankType, MiniQuote, Expression)
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


__all__ = [
    'UniverseSerializer', 'FractionSerializer', 'SideSerializer',
    'ArmySerializer', 'RankSerializer', 'RankTypeSerializer',
    'MiniQuoteSerializer', 'ExpressionSerializer'
]

FAILURE_MESSAGES = {
    'wrong_owner': _("You should use your own user id for owner field set"),
    'wrong_winner_rosters': _("There's no such winner `%s` in rosters")
}


class UniverseSerializer(serializers.HyperlinkedModelSerializer):
    codename = serializers.CharField(required=True)

    class Meta:
        model = Universe


class FractionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Fraction


class SideSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Side


class ArmySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Army


class RankSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Rank


class RankTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RankType


class MiniQuoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MiniQuote


class ExpressionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Expression
