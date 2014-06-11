# coding: utf-8
from apps.tabletop.models import Codex, Roster
from rest_framework import serializers


class CodexSerializer(serializers.HyperlinkedModelSerializer):
    content_type = serializers.SerializerMethodField('get_content_type')

    def get_content_type(self, instance):
        return instance.content_type.pk

    class Meta:
        model = Codex
        #exclude = ('content_type', )


class RosterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Roster