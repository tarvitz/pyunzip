# coding: utf-8
from apps.accounts.models import User
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'nickname', 'date_joined', 'avatar', 'gender',
            'is_active', 'email'
        )