from django.db.models.signals import (
    pre_save, post_save, pre_delete
)
from apps.wh.actions import rank_scheme_alter
from apps.wh.models import RankType, PM
from django.contrib.auth.models import User
from django.core.cache import get_cache, cache
from django.dispatch import receiver


def user_saved(instance, **kwargs):
    #print "user_saved function is active"
    rank_scheme_alter(instance,**kwargs)

#def user_post_save(instance, **kwargs):
#    cache.delete('nick:%s' % instance.username)
#    return instance
#
#def rank_type_save(instance, **kwargs):
#    # drop caches
#    users = User.objects.filter(
#        ranks__in=instance.rank_set.all()
#    )
#    for user in users:
#        cache.delete('nick:%s' % user.username)
#    return instance

@receiver(post_save, sender=User)
def on_user_change(instance, **kwargs):
    cache.set(
        'nick:%s' % instance.username,
        instance.get_nickname(no_cache=True)
    )
    return instance

@receiver(post_save, sender=RankType)
def on_rank_type_change(instance, **kwargs):
    users = User.objects.filter(
        ranks__in=instance.rank_set.all()
    )
    for user in list(users):
        cache.set(
            'nick:%s' % user.username,
            user.get_nickname(no_cache=True)
        )
    return instance

@receiver(pre_delete, sender=RankType)
def on_rank_type_delete(instance, **kwargs):
    return on_rank_type_change(instance, **kwargs)

@receiver(pre_save, sender=PM)
def on_pm_pre_save(instance, **kwargs):
    instance.cache_content = instance.render("content")
    return instance

def setup_signals():
    pre_save.connect(rank_scheme_alter,sender=User)
    #post_save.connect(user_post_save, sender=User)
    #post_save.connect(rank_type_save, sender=RankType)
