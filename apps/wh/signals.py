from django.db.models.signals import (
    pre_save, post_save, pre_delete
)

from apps.wh.models import RankType
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.core.cache import cache
from django.dispatch import receiver


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


def setup_signals():
    pass