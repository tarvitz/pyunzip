from apps.accounts.models import User
from django.db.models.signals import (
    post_save, pre_delete
)

from apps.wh.models import RankType
from apps.core.connections import get_redis_client
from django.dispatch import receiver


redis = get_redis_client()


@receiver(post_save, sender=User)
def on_user_change(instance, **kwargs):
    return instance


@receiver(post_save, sender=RankType)
def on_rank_type_change(instance, **kwargs):
    users = User.objects.filter(
        ranks__in=instance.rank_set.all()
    )
    for user in users:
        set_name = 'users:%s' % user.pk
        redis.hset(set_name, 'nickname', user.get_nickname())
    return instance


@receiver(pre_delete, sender=RankType)
def on_rank_type_delete(instance, **kwargs):
    return on_rank_type_change(instance, **kwargs)


def setup_signals():
    pass
