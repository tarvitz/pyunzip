from django.db.models.signals import pre_save, post_save, pre_delete
from apps.menu.models import HMenuItem, VMenuItem
from django.core.cache import get_cache, cache
from django.dispatch import receiver


#def hmenu_post_save(instance, **kwargs):
#    # drop caches
#    cache.delete('hmenu:all')
#    return instance

#def vmenu_post_save(instance, **kwargs):
#    # drop caches
#    cache.delete('vmenu:top')
#    return instance


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
    #post_save.connect(hmenu_post_save, sender=HMenuItem)
    #post_save.connect(vmenu_post_save, sender=VMenuItem)
    pass
