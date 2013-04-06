from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from apps.news.models import News
from django.core.mail import send_mail
from django.conf import settings

def pre_save_news(instance, **kwargs):
    if instance.approved:
        instance.status = 'approved'
    elif instance.status == 'rejected':
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
    return instance

def setup_signals():
    pre_save.connect(pre_save_news, sender=News)
