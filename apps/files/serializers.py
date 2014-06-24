# coding: utf-8
from apps.files.models import Gallery, Image, UserFile
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers


class GallerySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Gallery

class ImageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Image


class UserFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserFile
