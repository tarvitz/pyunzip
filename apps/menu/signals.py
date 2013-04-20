from django.db.models.signals import pre_save,post_save
from apps.menu.models import HMenuItem, VMenuItem
from django.core.cache import get_cache, cache

def hmenu_post_save(instance, **kwargs):
    # drop caches
    cache.delete('hmenu:all')
    return instance

def vmenu_post_save(instance, **kwargs):
    # drop caches
    cache.delete('vmenu:top')
    return instance

def setup_signals():
    post_save.connect(hmenu_post_save, sender=HMenuItem)
    post_save.connect(vmenu_post_save, sender=VMenuItem)
