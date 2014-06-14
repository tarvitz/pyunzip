# coding: utf-8
from apps.comments.models import CommentWatch, Comment
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class CommentWatchSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField('get_url')
    content_type = serializers.PrimaryKeyRelatedField()
    user = serializers.PrimaryKeyRelatedField()

    def get_url(self, instance):
        return instance.object.get_absolute_url()

    class Meta:
        model = CommentWatch
        fields = (
            'is_disabled', 'is_updated', 'url', 'id', 'content_type',
            'object_pk', 'user'
        )


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    content_type = serializers.PrimaryKeyRelatedField()
    site = serializers.PrimaryKeyRelatedField()
    submit_date = serializers.DateTimeField(required=False)
    user = serializers.HyperlinkedRelatedField(required=False,
                                               view_name='user-detail')

    def validate_user(self, attrs, source):
        request = self.context['request']
        privileged = request.user.has_perm('comments.change_comment')
        if not attrs[source]:
            return attrs

        if not privileged and attrs[source] != request.user:
            raise serializers.ValidationError(
                _("You can only post comment using your user id")
            )
        return attrs

    def restore_object(self, attrs, instance=None):
        if attrs.get('user') is None:
            attrs['user'] = self.context['request'].user
        return super(CommentSerializer, self).restore_object(attrs, instance)

    class Meta:
        model = Comment