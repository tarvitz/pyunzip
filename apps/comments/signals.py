# coding: utf-8

from django.db.models.signals import (
    pre_save,
)
from django.contrib.comments.models import Comment
from django.dispatch import receiver


@receiver(pre_save, sender=Comment)
def on_comment_pre_save(instance, **kwargs):
    instance.cache_comment = instance.render_comment()
    return instance


def setup_signals():
    pass