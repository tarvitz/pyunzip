# coding: utf-8
import django_filters
from apps.comments.models import CommentWatch
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from django.http import Http404
from apps.comments.serializers import CommentWatchSerializer


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
    filter_fields = ('is_updated', 'is_disabled', 'id')

    def get_queryset(self):
        qs = super(CommentWatchViewSet, self).get_queryset()
        if self.request.user.is_authenticated():
            return qs.filter(user=self.request.user)
        return CommentWatch.objects.none()


class CommentWatchDetail(APIView):
    """
    Retrieve, update or delete a CommentWatch instance.
    """

    def get_object(self, pk):
        try:
            return CommentWatch.objects.get(pk=pk)
        except CommentWatch.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        comment_watch = self.get_object(pk)
        serializer = CommentWatchSerializer(comment_watch)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        comment_watch = self.get_object(pk)
        serializer = CommentWatchSerializer(comment_watch, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        comment_watch = self.get_object(pk)
        comment_watch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)