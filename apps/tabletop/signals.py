# coding: utf-8
from datetime import datetime, timedelta

from django.conf import settings
from django.db.models.signals import (
    post_save, pre_save, post_delete, pre_delete
)
from django.db.models import F

from django.contrib.auth.models import User
from apps.tabletop.models import (
    WargearContainer, UnitContainer, Wargear, BattleReport
)
from apps.core.helpers import get_object_or_None
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver


def wargear_container_pre_save(instance, **kwargs):
    if instance.link.is_squad_only:
        instance.amount = instance.unit.amount
    instance.reload_pts(rebuild=True)
    return instance

def wargear_container_post_save(instance, **kwargs):
    if not instance.link.is_squad_only:
        instance.unit.reload_pts(rebuild=True, commit=True)
    return instance

def wargear_container_post_delete(instance, **kwargs):
    instance.unit.reload_pts(rebuild=True, commit=True)
    #pass

def unit_container_pre_save(instance, **kwargs):
    #if instance.pk:
    instance.reload_pts(rebuild=True)
    return instance

def unit_container_post_save(instance, **kwargs):
    squad_only = instance.wargear_containers.filter(link__is_squad_only=True)
    resave = False
    if squad_only:
        for wargear in squad_only:
            if wargear.amount != instance.amount:
                resave = True
                wargear.save()
    if resave:
        # force recount of total model pts
        instance.save()
    return instance

def wargear_pre_save(instance, **kwargs):
    instance = instance.generate_short_title()
    return instance

#def battle_report_post_save(instance, **kwargs):
#    cache.delete('tabletop:report:%s' % instance.pk)
#    return instance

@receiver(post_save, sender=BattleReport)
def on_battle_report_change(instance, **kwargs):
    cache.set('tabletop:report:%s' % instance.pk, instance)
    return instance

@receiver(pre_delete, sender=BattleReport)
def on_battle_report_delete(instance, **kwargs):
    cache.delete('tabletop:report:%s' % instance.pk)
    return instance

def setup_signals():
    # pre saves
    pre_save.connect(wargear_pre_save, sender=Wargear)
    pre_save.connect(unit_container_pre_save, sender=UnitContainer)
    pre_save.connect(wargear_container_pre_save, sender=WargearContainer)
    # post saves
    post_save.connect(wargear_container_post_save, sender=WargearContainer)
    post_save.connect(unit_container_post_save, sender=UnitContainer)
    # post deletes
    post_delete.connect(wargear_container_post_delete, sender=WargearContainer)
    #post_save.connect(battle_report_post_save, sender=BattleReport)
