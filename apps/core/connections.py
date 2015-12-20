# -*- coding: utf-8 -*-
"""
.. module:: apps.core.connections
    :synopsis: Connections issues
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import redis
from django.conf import settings


#: closure get redis client
def _get_redis_client():
    """
    get redis client

    :rtype: redis.client.StrictRedis
    :return: client
    """
    return redis.StrictRedis(**settings.REDIS)


def _get_redis_connector():
    client = None

    def closure():
        nonlocal client
        if not client:
            client = _get_redis_client()
        return client
    return closure
redis_connector = _get_redis_connector()


def get_redis_client():
    return redis_connector()
