from django.db.models.signals import (
    pre_save, post_save, pre_delete
)
from django.utils.translation import ugettext_lazy as _
from apps.news.models import News, Event
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.dispatch import receiver
from datetime import datetime, timedelta


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
    return instance


@receiver(pre_save, sender=News)
def on_news_pre_save(instance, **kwargs):
    instance.cache_content = instance.render_content()
    if instance.approved:
        instance.status = 'approved'
    return instance


@receiver(pre_save, sender=Event)
def on_event_pre_save(instance, **kwargs):
    instance.content_html = instance.render_content()
    if not instance.date_end:
        instance.date_end = (
            datetime(*instance.date_start.timetuple()[:3]) +
            timedelta(hours=23, minutes=59)
        )
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

    pass
