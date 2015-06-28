from django.db.models.signals import post_save
from apps.pybb.subscription import (
    notify_topic_subscribers, notify_pm_recipients)
from apps.pybb.models import Post


def post_saved(instance, **kwargs):
    notify_topic_subscribers(instance)

def pm_saved(instance, **kwargs):
    notify_pm_recipients(instance)


def setup_signals():
    post_save.connect(post_saved, sender=Post)
