# coding: utf-8
import django_filters
from apps.accounts.models import User
from rest_framework import viewsets
from apps.accounts.serializers import UserSerializer


class UserFilterSet(django_filters.FilterSet):
    class Meta:
        model = User


class UserViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for event
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_class = UserSerializer
