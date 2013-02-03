from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from apps.news.models import News

def pre_save_news(instance, **kwargs):
    if instance.approved:
        instance.status = 'approved'
    return instance

def setup_signals():
    pre_save.connect(pre_save_news, sender=News)

