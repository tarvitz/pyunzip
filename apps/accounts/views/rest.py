# coding: utf-8
import django_filters
from apps.accounts.models import User
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from apps.accounts.serializers import UserSerializer


class UserFilterSet(django_filters.FilterSet):
    class Meta:
        model = User


class UserCRUDAccessMixin(object):
    def create(self, request, *args, **kwargs):
        if (request.user.is_authenticated()
                and request.user.has_perm('accounts.change_user')):
            return super(UserCRUDAccessMixin, self).create(request, *args,
                                                           **kwargs)

        serializer = super(UserCRUDAccessMixin, self).get_serializer(
            data=request.DATA, files=request.FILES)
        errors = {
            request.method.lower(): 'permission denied'
        }
        errors.update(serializer.errors)
        return Response(errors, status=status.HTTP_403_FORBIDDEN)

    def update(self, request, *args, **kwargs):
        if (request.user.is_authenticated()
                and request.user.has_perm('accounts.change_user')):
            return super(UserCRUDAccessMixin, self).update(request, *args,
                                                           **kwargs)
        serializer = super(UserCRUDAccessMixin, self).get_serializer(
            data=request.DATA, files=request.FILES)
        errors = {
            request.method.lower(): 'permission denied'
        }
        errors.update(serializer.errors)
        return Response(errors, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if (request.user.is_authenticated()
                and request.user.has_perm('accounts.change_user')):
            return super(UserCRUDAccessMixin, self).destroy(request, *args,
                                                            **kwargs)
        serializer = super(UserCRUDAccessMixin, self).get_serializer(
            data=request.DATA, files=request.FILES)
        errors = {
            request.method.lower(): 'permission denied'
        }
        errors.update(serializer.errors)
        return Response(errors, status=status.HTTP_403_FORBIDDEN)


class UserViewSet(UserCRUDAccessMixin, viewsets.ModelViewSet):
    """
    API viewpoint for event
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # filter_class = UserSerializer


    def get_queryset(self):
        qs = super(UserViewSet, self).get_queryset()
        if self.request.user.is_authenticated():

            return (
                qs if self.request.user.has_perm('accounts.change_user')
                else qs.filter(pk=self.request.user.pk)
            )
        return qs.none()