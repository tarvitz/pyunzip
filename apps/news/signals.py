from django.db.models.signals import (
    pre_save, post_save, pre_delete
)
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from apps.news.models import News
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver


def pre_save_news(instance, **kwargs):
    if instance.approved:
        instance.status = 'approved'
    elif instance.status == 'revision' and instance.resend:
        if settings.SEND_MESSAGES and instance.owner.email:
            kw = {
                'reason': instance.reason
            }
            send_mail(
                subject=_("Your article changed status"),
                message=settings.ARICLE_REJECTED_NOTIFICATION % kw,
                from_email=settings.FROM_EMAIL,
                recipient_list=[instance.owner.email, ],
                fail_silently=True
            )
            instance.resend = False
    instance.cache_content = instance.render("content")
    return instance

@receiver(post_save, sender=News)
def on_news_change(instance, **kwargs):
    cache.delete('news:all:admin')
    cache.delete('news:all:everyone')
    return instance

@receiver(pre_delete, sender=News)
def on_news_delete(instance, **kwargs):
    cache.delete('news:all:admin')
    cache.delete('news:all:everyone')

def setup_signals():
    #pre_save.connect(pre_save_news, sender=News)
    pass
