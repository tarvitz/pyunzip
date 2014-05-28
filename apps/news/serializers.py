# coding: utf-8
from apps.news.models import Event
from rest_framework import serializers


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = ('title', 'date_start', 'date_end', 'type', 'is_finished')
