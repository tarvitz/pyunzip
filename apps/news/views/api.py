# coding: utf-8
import django_filters
from apps.news.models import Event
from rest_framework import viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from apps.news.serializers import EventSerializer


class EventPermission(BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True
        return request.user.has_perm('news.change_event')


class EventFilterSet(django_filters.FilterSet):
    date_start = django_filters.DateTimeFilter(lookup_type='gte')
    date_end = django_filters.DateTimeFilter(lookup_type='lte')

    class Meta:
        model = Event


class EventViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for event
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_class = EventFilterSet
    filter_fields = ('date_start', 'date_end', 'title', )
    permission_classes = (EventPermission, )
