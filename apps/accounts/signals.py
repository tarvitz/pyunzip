# coding: utf-8
from apps.accounts.models import PM

from django.dispatch import receiver
from django.db.models.signals import (
    pre_save,
)

__all__ = ['on_pm_pre_save', ]


@receiver(pre_save, sender=PM)
def on_pm_pre_save(instance, **kwargs):
    instance.cache_content = instance.render("content")
    return instance


def setup_run():
    pass
