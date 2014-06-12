# coding: utf-8
from apps.karma.models import Karma

from django.dispatch import receiver
from django.db.models.signals import (
    pre_save, post_save, pre_delete
)

__all__ = ['on_karma_post_save', ]


@receiver(post_save, sender=Karma)
def on_karma_post_save(instance, **kwargs):
    amount = instance.user.get_karma_value()
    if instance.user.karma != amount:
        instance.user.karma = amount
        instance.user.save()
    return instance


def setup_run():
    pass
