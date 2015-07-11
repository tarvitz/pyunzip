# coding: utf-8
from apps.accounts.models import User, PM, PolicyWarning
from apps.core.serializers import CurrentUserSerializerMixin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers


class AccountSerializer(serializers.HyperlinkedModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group, required=False
    )
    user_permissions = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Permission, required=False
    )

    class Meta:
        model = User
        exclude = ('password', )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'nickname', 'date_joined', 'avatar', 'gender',
            'is_active',
        )


class PMSerializer(CurrentUserSerializerMixin,
                   serializers.HyperlinkedModelSerializer):
    sender = serializers.HyperlinkedRelatedField(
        required=False, read_only=False,
        view_name='user-detail', queryset=User.objects
    )

    check_fields = ['sender', ]
    check_permission = 'accounts.change_pm'

    def update(self, instance, validated_data):
        self._process_validated_data(validated_data)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.save()
        return instance

    def create(self, validated_data):
        self._process_validated_data(validated_data)
        return PM.objects.create(**validated_data)

    def validate_addressee(self, value):
        if value == self.context['request'].user:
            raise serializers.ValidationError(
                _("You can not send pm for yourself")
            )
        return value

    class Meta:
        model = PM


class PolicyWarningSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PolicyWarning
