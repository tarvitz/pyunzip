# -*- coding: utf-8 -*-
"""
.. module:: apps.accounts.apps
    :synopsis: App config
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'apps.accounts'
    verbose_name = _('Accounts Application Module')

    def ready(self):
        from .signals import setup_signals
        setup_signals()
