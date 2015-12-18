# -*- coding: utf-8 -*-
"""
.. module:: apps.comments.apps
    :synopsis: App config
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""

import redis

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


class CommentConfig(AppConfig):
    name = 'apps.comments'
    verbose_name = _('Comments Application Module')

    def ready(self):
        from .signals import setup_signals
        setup_signals()
        #: redis client
        self.redis_db = redis.StrictRedis(**settings.REDIS)
