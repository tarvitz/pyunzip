# coding: utf-8
import django_filters
from apps.news.models import Event
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from apps.news.serializers import EventSerializer


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
    permission_classes = (AllowAny, )
