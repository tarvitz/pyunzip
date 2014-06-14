# coding: utf-8
from django.conf import settings
from apps.core.helpers import render_filter
from django.db.models.signals import (
    post_save, pre_delete, pre_save
)
from apps.tabletop.models import (
    BattleReport, Roster
)
from django.dispatch import receiver


@receiver(post_save, sender=BattleReport)
def on_battle_report_change(instance, **kwargs):
    if instance.approved:
        for roster in instance.rosters.all():
            roster.reload_wins_defeats()
    return instance


@receiver(pre_delete, sender=BattleReport)
def on_battle_report_delete(instance, **kwargs):
    return instance


@receiver(pre_save, sender=Roster)
def on_roster_pre_save(instance, **kwargs):
    instance.roster_cache = render_filter(instance.roster, instance.syntax or
                                          settings.DEFAULT_SYNTAX)
    return instance


def setup_signals():
    pass