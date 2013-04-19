from django.db.models.signals import pre_save,post_save
from apps.wh.actions import rank_scheme_alter
from apps.wh.models import RankType
from django.contrib.auth.models import User
from django.core.cache import get_cache, cache

def user_saved(instance, **kwargs):
    #print "user_saved function is active"
    rank_scheme_alter(instance,**kwargs)

def user_post_save(instance, **kwargs):
    cache.delete('nick:%s' % instance.username)
    return instance

def rank_type_save(instance, **kwargs):
    # drop caches
    users = User.objects.filter(
        ranks__in=instance.rank_set.all()
    )
    for user in users:
        cache.delete('nick:%s' % user.username)
    return instance

def setup_signals():
    pre_save.connect(rank_scheme_alter,sender=User)
    post_save.connect(user_post_save, sender=User)
    post_save.connect(rank_type_save, sender=RankType)
