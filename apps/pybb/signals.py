from django.dispatch import receiver
from django.db.models.signals import post_save

from . import subscription, models


def pm_saved(instance, **kwargs):
    subscription.notify_pm_recipients(instance)


@receiver(post_save, sender=models.Post)
def on_comment_post_sve(instance, **kwargs):
    subscription.notify_topic_subscribers(instance)
    instance.update_rank()


def setup_signals():
    pass
