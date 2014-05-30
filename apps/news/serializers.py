# coding: utf-8
from apps.news.models import Event
from rest_framework import serializers


class EventSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('get_url')

    def get_url(self, instance):
        return instance.get_absolute_url()

    class Meta:
        model = Event
        fields = (
            'title', 'date_start', 'date_end', 'type', 'is_finished', 'url',
            'is_all_day', 'league'
        )
