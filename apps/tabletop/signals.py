# coding: utf-8
from django.conf import settings
from apps.core.helpers import render_filter
from django.db.models.signals import (
    pre_delete, pre_save
)
from apps.tabletop.models import (
    Report, Roster
)
from django.dispatch import receiver


@receiver(pre_save, sender=Report)
def on_report_pre_save(instance, **kwargs):
    instance.comment_cache = instance.render_comment()
    return instance


@receiver(pre_delete, sender=Report)
def on_report_delete(instance, **kwargs):
    return instance


@receiver(pre_save, sender=Roster)
def on_roster_pre_save(instance, **kwargs):
    instance.roster_cache = render_filter(instance.roster, instance.syntax or
                                          settings.DEFAULT_SYNTAX)
    return instance


def setup_signals():
    pass
