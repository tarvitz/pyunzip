from django.db.models.signals import post_save, pre_delete
from apps.menu.models import HMenuItem, VMenuItem
from django.core.cache import cache
from django.dispatch import receiver


@receiver(post_save, sender=HMenuItem)
def on_change_hmenu(instance, **kwargs):
    cache.delete('hmenu:all')
    return instance


@receiver(post_save, sender=VMenuItem)
def on_change_vmenu(instance, **kwargs):
    cache.delete('vmenu:top')
    return instance


@receiver(pre_delete, sender=HMenuItem)
def on_delete_hmenu(instance, **kwargs):
    cache.delete('hmenu:all')
    return instance


@receiver(pre_delete, sender=VMenuItem)
def on_delete_vmenu(instance, **kwargs):
    cache.delete('hmenu:top')
    return instance


def setup_signals():
    pass
