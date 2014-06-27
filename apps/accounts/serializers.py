# coding: utf-8
from apps.accounts.models import User, PM, PolicyWarning
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(many=True)
    user_permissions = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = User
        exclude = ('password', )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'nickname', 'date_joined', 'avatar', 'gender',
            'is_active', 'email'
        )


class PMSerializer(serializers.HyperlinkedModelSerializer):
    sender = serializers.HyperlinkedRelatedField(required=False,
                                                 view_name='user-detail')

    def restore_object(self, attrs, instance=None):
        if not attrs.get('sender'):
            attrs['sender'] = self.context['request'].user
        return super(PMSerializer, self).restore_object(attrs, instance)

    def save_object(self, obj, **kwargs):
        request = self.context['request']
        if not request.user.has_perm('accounts.change_pm'):
            obj.sender = request.user
        return super(PMSerializer, self).save_object(obj, **kwargs)

    def validate_addressee(self, attrs, source):
        if attrs[source] == self.context['request'].user:
            raise serializers.ValidationError(
                _("You can not send pm for yourself")
            )
        return attrs

    class Meta:
        model = PM


class PolicyWarningSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PolicyWarning