# -*- coding: utf-8 -*-
"""
.. module:: apps.comments.utils
    :synopsis: Utils
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from django.apps import apps
from django.contrib.contenttypes.models import ContentType
from . import models


def get_redis_client():
    """
    get redis client

    :rtype: redis.client.StrictRedis
    :return: client
    """
    return apps.get_app_config('comments').redis_db


def get_redis_set_name(content_object):
    """
    get redis unique set name

    :param django.db.models.Model content_object: instance
    :rtype: str
    :return: set name
    """
    return '%(app_label)s.%(model_name)s.%(pk)s' % {
        'app_label': content_object._meta.app_label,
        'model_name': content_object._meta.model_name,
        'pk': content_object.pk
    }


def get_comment_position(content_object, comment_pk):
    """
    get comment position (rank or ranking) according to content object
    whole set of comments

    :param django.db.models.Model content_object: some model instance
        for example apps.news.models.News
    :param int comment_pk: comment primary key
    :rtype: int
    :return: rank
    """
    client = get_redis_client()
    set_name = get_redis_set_name(content_object)
    return client.zrevrank(set_name, comment_pk)


def get_count(content_object):
    """
    get count for comments in set

    :param django.db.models.Model content_object: some model instance
    :rtype: int
    :return: count
    """
    client = get_redis_client()
    return client.zcount(get_redis_set_name(content_object), '-inf', 'inf')


def store_comment_positions(content_object):
    """
    store ranks (rankings) for comments

    :param django.db.models.Model content_object: some model instance
    :rtype: None
    :return: None
    """
    app_content_type = ContentType.objects.get_for_model(content_object)
    comments = models.Comment.objects.filter(
            content_type=app_content_type, object_pk=content_object.pk
    ).order_by('-pk')
    redis_client = get_redis_client()
    set_name = get_redis_set_name(content_object)
    zadd = redis_client.zadd

    for rank, comment_pk in enumerate(comments.values_list('pk', flat=True)):
        zadd(set_name, *(rank, str(comment_pk)))
