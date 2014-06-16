# coding: utf-8
from apps.news.models import Event, EventWatch
from rest_framework import serializers


class EventSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('get_url')
    is_new = serializers.SerializerMethodField('get_is_new')
    place = serializers.PrimaryKeyRelatedField()
    icon = serializers.SerializerMethodField('get_icon')

    def get_url(self, instance):
        return instance.get_absolute_url()

    def get_icon(self, instance):
        leagues = ['wh40k', ]
        classes = ['chsr-aquila', ]
        pattern = '<i class="%(class)s"></i>'
        if instance.league in leagues:
            return pattern % {'class': classes[leagues.index(instance.league)]}
        return ''

    def get_is_new(self, instance):
        user = self.context['request'].user
        # instance is finished is prior any of watch marks
        if not instance.is_finished and user.is_authenticated():
            return not bool(EventWatch.objects.filter(
                event=instance, user=user).count())
        return False

    class Meta:
        model = Event
        fields = (
            'title', 'date_start', 'date_end', 'type', 'is_finished', 'url',
            'is_all_day', 'is_new', 'league', 'place', 'icon', 'id',
            #'content'  # currently disabled
        )
