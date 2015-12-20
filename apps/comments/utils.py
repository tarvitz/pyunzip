# -*- coding: utf-8 -*-
"""
.. module:: apps.comments.utils
    :synopsis: Utils
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from apps.core.connections import get_redis_client

from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType


def get_redis_set_name(content_object):
    """
    get redis unique set name

    :param django.db.models.Model content_object: instance
    :rtype: str
    :return: set name
    """
    return '%(app_label)s.%(model_name)s.comment.%(pk)s' % {
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
    return client.zrank(set_name, comment_pk)


def get_count(content_object):
    """
    get count for comments in set

    :param django.db.models.Model content_object: some model instance
    :rtype: int
    :return: count
    """
    client = get_redis_client()
    return client.zcount(get_redis_set_name(content_object), '-inf', 'inf')


def get_page(rank, objects_on_page=None):
    """
    get comment page according to its rank (meaning position or so)

    :param int rank: comment rank
    :param int | None objects_on_page: objects on page if None
        use settings.OBJECTS_ON_PAGE
    :rtype: int
    :return: int
    """
    objects_on_page = (objects_on_page or settings.OBJECTS_ON_PAGE) or 1
    rank = rank or 1
    page = int(rank / objects_on_page)
    if rank % objects_on_page > 0:
        return page + 1
    return page


def store_comment_positions(content_object):
    """
    store ranks (rankings) for comments

    :param django.db.models.Model content_object: some model instance
    :rtype: None
    :return: None
    """
    comment_model = apps.get_model(app_label='comments', model_name='comment')
    app_content_type = ContentType.objects.get_for_model(content_object)
    comments = comment_model.objects.filter(
            content_type=app_content_type, object_pk=content_object.pk
    ).order_by('pk')
    redis_client = get_redis_client()
    set_name = get_redis_set_name(content_object)
    zadd = redis_client.zadd

    for rank, comment_pk in enumerate(comments.values_list('pk', flat=True)):
        zadd(set_name, *(rank, str(comment_pk)))


def zadd(comment, rank=None):
    """
    add instance to rankings

    :param apps.comments.models.Comment comment: comment instance
    :param None | int rank: rank
    :rtype: None
    :return: None
    """
    comment_pk = str(comment.pk)
    set_name = get_redis_set_name(comment.content_object)
    comment_model = apps.get_model(app_label='comments', model_name='comment')

    redis_client = get_redis_client()
    has_rank = redis_client.zrank(set_name, comment_pk)
    if has_rank is None:
        rank = (
            rank or comment_model.objects.filter(
                    content_type=comment.content_type,
                    object_pk=comment.content_object.pk
            ).count()
        )
        redis_client.zadd(set_name, *(rank, comment_pk))
