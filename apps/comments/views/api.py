# coding: utf-8
import django_filters
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from django.http import Http404

from apps.comments.serializers import CommentWatchSerializer
from apps.comments.models import CommentWatch


class CommentWatchFilterSet(django_filters.FilterSet):
    is_updated = django_filters.BooleanFilter(lookup_type='exact')
    is_disabled = django_filters.BooleanFilter(lookup_type='exact')
    id = django_filters.AllValuesFilter()

    class Meta:
        model = CommentWatch


class CommentWatchViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for CommentWatch instance
    """
    queryset = CommentWatch.objects.all()
    serializer_class = CommentWatchSerializer
    filter_class = CommentWatchFilterSet
    filter_fields = (
        'is_updated', 'is_disabled', 'id',
    )

    def update(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            try:
                self.get_object()
                return super(CommentWatchViewSet, self).update(request, *args,
                                                               **kwargs)
            except Http404:
                serializer = super(CommentWatchViewSet, self).get_serializer(
                    data=request.DATA, files=request.FILES)
                errors = {
                    'detail': 'Not allowed.'
                }
                errors.update(serializer.errors)
                return Response(errors, status=status.HTTP_403_FORBIDDEN)

    def get_queryset(self):
        qs = super(CommentWatchViewSet, self).get_queryset()
        if self.request.user.is_authenticated():
            return (
                qs if self.request.user.has_perm(
                    'comments.change_commentwatch')
                else qs.filter(user=self.request.user)
            )
        return CommentWatch.objects.none()
