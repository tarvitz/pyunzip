# coding: utf-8
from apps.accounts.models import User
from apps.core.serializers import (
    ModelAccessSerializerMixin, CurrentUserSerializerMixin)
from apps.comments.models import CommentWatch, Comment
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
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
                        CurrentUserSerializerMixin,
                        serializers.HyperlinkedModelSerializer):
    user_owner_fields = ['user', ]

    url = serializers.HyperlinkedIdentityField(
        view_name='comment-detail',
        lookup_field='pk'
    )
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects
    )
    site = serializers.PrimaryKeyRelatedField(queryset=Site.objects)
    submit_date = serializers.DateTimeField(required=False)
    user = serializers.HyperlinkedRelatedField(
        required=False, default=None, queryset=User.objects,
        view_name='user-detail'
    )

    check_fields = ['user']
    check_permission = 'comments.change_comment'

    def validate_user(self, value):
        request = self.context['request']
        privileged = request.user.has_perm('comments.change_comment')
        if not value:
            return request.user if value is None else value

        if not privileged and value != request.user:
            raise serializers.ValidationError(
                _("You can only post comment using your user id")
            )
        return value

    def update(self, instance, validated_data):
        self._process_validated_data(validated_data)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

    class Meta:
        model = Comment
        exclude = ('user_name', 'user_email', 'user_url', 'ip_address', )


class ModifyCommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comment
        fields = ('comment', 'syntax', )
