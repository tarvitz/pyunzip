# coding: utf-8
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from datetime import datetime


# Create your models here.
class Karma(models.Model):
    comment = models.CharField(_('Comment'), max_length=512, blank=True)
    value = models.IntegerField(_('Power'))
    date = models.DateTimeField(_('Date'), default=datetime.now)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='karma_user_set',
                             verbose_name=_("user"))
    voter = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='karma_voter_set',
                              verbose_name=_("voter"))
    url = models.URLField(_('URL'), blank=True, null=True)

    def get_user_karma_url(self):
        return reverse('karma:karma-list', args=(self.user.pk, ))

    def get_absolute_url(self):
        return reverse('karma:karma-detail', args=(self.pk, ))

    class Meta:
        ordering = ['-date']


from .signals import setup_run
setup_run()
