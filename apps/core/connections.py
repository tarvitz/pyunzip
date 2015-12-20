# -*- coding: utf-8 -*-
"""
.. module:: apps.core.connections
    :synopsis: Connections issues
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from django.apps import apps


#: closure get redis client

def _get_redis_client():
    """
    get redis client

    :rtype: redis.client.StrictRedis
    :return: client
    """
    return apps.get_app_config('core').redis_db


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
