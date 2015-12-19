# -*- coding: utf-8 -*-
"""
.. module:: apps.core.apps
    :synopsis: App config
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
import redis

from django.apps import AppConfig
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


class CoreConfig(AppConfig):
    name = 'apps.core'
    verbose_name = _('Core Application Module')

    def ready(self):
        from .signals import setup_signals
        setup_signals()
        self.redis_db = redis.StrictRedis(**settings.REDIS)
