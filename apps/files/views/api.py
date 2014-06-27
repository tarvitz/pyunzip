# coding: utf-8

from apps.files.models import Gallery, Image, UserFile
from apps.core.api import IsOwnerOrModelAdminOrReadOnly
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import parsers
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
    parser_classes = (parsers.FormParser, parsers.MultiPartParser,
                      parsers.JSONParser)
    permission_classes = (IsOwnerOrModelAdminOrReadOnly, )


class UserFileViewSet(viewsets.ModelViewSet):
    queryset = UserFile.objects.all()
    serializer_class = UserFileSerializer
    permission_classes = (IsOwnerOrModelAdminOrReadOnly, )
