# coding: utf-8
from apps.core.serializers import ModelAccessSerializerMixin
from apps.comments.models import CommentWatch, Comment
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _


class CommentWatchSerializer(ModelAccessSerializerMixin,
                             serializers.HyperlinkedModelSerializer):
    user_owner_fields = ['user', ]

    url = serializers.SerializerMethodField('get_self_url')

    def get_self_url(self, instance):
        if hasattr(instance.object, 'get_absolute_url'):
            return instance.object.get_absolute_url()
        return ''

    class Meta:
        model = CommentWatch


class CommentSerializer(ModelAccessSerializerMixin,
                        serializers.HyperlinkedModelSerializer):
    user_owner_fields = ['user', ]

    content_type = serializers.PrimaryKeyRelatedField(read_only=True)
    site = serializers.PrimaryKeyRelatedField(read_only=True)
    submit_date = serializers.DateTimeField(required=False)
    user = serializers.HyperlinkedRelatedField(required=False,
                                               read_only=True,
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
        exclude = ('user_name', 'user_email', 'user_url', 'ip_address', )


class ModifyCommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ('comment', 'syntax', )