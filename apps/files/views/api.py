# coding: utf-8

from apps.files.models import Gallery, Image, UserFile
from rest_framework import viewsets
from rest_framework import permissions

from apps.files.serializers import (
    GallerySerializer, ImageSerializer, UserFileSerializer
)


class GalleryViewSet(viewsets.ModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )


class UserFileViewSet(viewsets.ModelViewSet):
    queryset = UserFile.objects.all()
    serializer_class = UserFileSerializer
    permission_classes = (permissions.DjangoModelPermissionsOrAnonReadOnly, )
