# coding: utf-8
from apps.core.serializers import ModelAccessSerializerMixin
from apps.files.models import Gallery, Image, UserFile
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class GallerySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Gallery


class ImageSerializer(ModelAccessSerializerMixin,
                      serializers.HyperlinkedModelSerializer):
    user_owner_fields = ['owner', ]

    class Meta:
        model = Image


class UserFileSerializer(ModelAccessSerializerMixin,
                         serializers.HyperlinkedModelSerializer):
    user_owner_fields = ['owner', ]

    class Meta:
        model = UserFile
