# coding: utf-8
from .models import (
    Post, Topic, Poll, PollAnswer, PollItem, Forum, Category, Read
)
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _

FAILURE_MESSAGES = {
    'self_karma_set': _("You can not alter karma for yourself"),
    'karma_amount_exceed': _(
        "You can not set custom karma amount, use `-1` and `1` values only."
    ),
    'timeout': _(
        "Timeout. You have exceeded amount of karma modification, please wait"
    ),
    'karma_voter_violation': _(
        "You can not set another user for voting. Use your own id",
    )
}

__all__ = [
    'FAILURE_MESSAGES', 'ForumSerializer', 'PostSerializer',
    'TopicSerializer', 'PollSerializer', 'PollAnswerSerializer',
    'PollItemSerializer', 'CategorySerializer', 'ReadSerializer'
]


class ForumSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Forum


class PostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Post


class TopicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Topic


class PollSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Poll


class PollAnswerSerializer(serializers.HyperlinkedModelSerializer):
    class Model:
        model = PollAnswer


class PollItemSerializer(serializers.HyperlinkedModelSerializer):
    class Model:
        model = PollItem


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category


class ReadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Read
