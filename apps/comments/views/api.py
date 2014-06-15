# coding: utf-8
import django_filters
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import exceptions
from rest_framework.decorators import action
from django.http import Http404

from apps.comments.serializers import (
    CommentWatchSerializer, CommentSerializer,
    ModifyCommentSerializer
)
from apps.comments.models import CommentWatch, Comment


__all__ = ['CommentWatchViewSet', 'CommentViewSet']


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


class CommentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # GET, HEAD, OPTION is allowed for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        privileged = request.user and request.user.has_perm(
            'comments.change_comment')
        if obj.user == request.user or privileged:
            return True
        return False


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (CommentPermission, )

    @action(methods=['PATCH', 'PUT', ])
    def modify(self, request, pk=None):
        obj = self.get_object_or_none()
        serializer = ModifyCommentSerializer(data=request.DATA, instance=obj)
        if serializer.is_valid():
            serializer.save()
            state = (
                status.HTTP_200_OK if obj.pk == serializer.object.pk
                else status.HTTP_201_CREATED
            )
            return Response(serializer.data, status=state)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        privileged = request.user and request.user.has_perm(
            'comments.change_comment')

        if all((not privileged, request.user == obj.user,
                request.method == 'PUT')):
            raise exceptions.PermissionDenied()
        return super(CommentViewSet, self).update(request, *args, **kwargs)