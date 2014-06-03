# coding: utf-8
from apps.comments.models import CommentWatch
from rest_framework import serializers


class CommentWatchSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('get_url')

    def get_url(self, instance):
        return instance.object.get_absolute_url()

    class Meta:
        model = CommentWatch
        fields = (
            'is_disabled', 'is_updated', 'url', 'id'
        )
