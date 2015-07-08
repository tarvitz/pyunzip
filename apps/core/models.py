# coding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings

from datetime import datetime

from apps.core.managers import UserSIDManager


@python_2_unicode_compatible
class UserSID(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='user_sid_set')
    sid = models.CharField(_("SID"), unique=True, max_length=512)
    # additional fields ?
    expired_date = models.DateTimeField(
        _("Expires"),
    )
    expired = models.BooleanField(
        _("expired?"), default=False
    )
    created_on = models.DateTimeField(
        _("created on"), auto_now_add=True,
    )
    updated_on = models.DateTimeField(
        _('updated on'), default=datetime.now
    )
    objects = UserSIDManager()

    def __str__(self):
        return "%s [%s]" % (self.user.username, self.sid)

    class Meta:
        verbose_name = _("UserSID")
        verbose_name_plural = _("UserSIDs")


from apps.core import signals
signals.setup_signals()
