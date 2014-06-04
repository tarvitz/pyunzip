# coding: utf-8

from django.db.models.signals import (
    post_save, pre_delete
)
from apps.tabletop.models import (
    BattleReport,
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

def setup_signals():
    pass