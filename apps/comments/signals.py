# coding: utf-8

from django.db.models.signals import (
    pre_save, post_save
)
from . import models, utils
from django.dispatch import receiver


@receiver(pre_save, sender=models.Comment)
def on_comment_pre_save(instance, **kwargs):
    instance.cache_comment = instance.render_comment()
    return instance


@receiver(post_save, sender=models.Comment)
def on_comment_post_sve(instance, **kwargs):
    utils.zadd(instance)


def setup_signals():
    pass
