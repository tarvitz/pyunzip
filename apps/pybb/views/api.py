# coding: utf-8
from rest_framework import viewsets
from ..serializers import (
    CategorySerializer, ForumSerializer, TopicSerializer, PostSerializer,
    ReadSerializer, PollSerializer, PollItemSerializer, PollAnswerSerializer
)
from apps.core.api import IsModelAdminOrReadOnly
from ..models import (
    Category, Forum, Topic, Post, Read, Poll, PollItem, PollAnswer)

__all__ = ['CategoryViewSet', ]


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for Karma instance
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsModelAdminOrReadOnly, )


class ForumViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for Karma instance
    """
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    permission_classes = (IsModelAdminOrReadOnly, )


class TopicViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for Karma instance
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = (IsModelAdminOrReadOnly, )


class PostViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for Karma instance
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsModelAdminOrReadOnly, )


class ReadViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for Karma instance
    """
    queryset = Read.objects.all()
    serializer_class = ReadSerializer
    permission_classes = (IsModelAdminOrReadOnly, )


class PollViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for Karma instance
    """
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = (IsModelAdminOrReadOnly, )


class PollItemViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for Karma instance
    """
    queryset = PollItem.objects.all()
    serializer_class = PollItemSerializer
    permission_classes = (IsModelAdminOrReadOnly, )


class PollAnswerViewSet(viewsets.ModelViewSet):
    """
    API viewpoint for Karma instance
    """
    queryset = PollAnswer.objects.all()
    serializer_class = PollAnswerSerializer
    permission_classes = (IsModelAdminOrReadOnly, )
