# coding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class HMenuItem(models.Model):
    title = models.CharField(_("title"), max_length=256)
    order = models.PositiveSmallIntegerField(
        _("Order"),
        help_text=_("Less is prior"), default=0)
    attrs = models.CharField(
        _('attributes'), max_length=1024,
        blank=True, null=True
    )
    url = models.CharField(
        _("URL"), max_length=256,
        null=True, blank=True
    )
    is_hidden = models.BooleanField(
        _("is hidden"),
        help_text=_("marks menu item as hidden"),
        default=False)

    def get_url(self):
        return self.url

    def get_absolute_url(self):
        return self.get_url()

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Horizontal Menu")
        verbose_name_plural = _("Horizontal Menus")
        ordering = ['order', 'id', ]


@python_2_unicode_compatible
class VMenuItem(models.Model):
    title = models.CharField(_("Title"), max_length=256)
    order = models.PositiveSmallIntegerField(
        _("Order"),
        help_text=_("Less is prior"), default=0)
    # blank means top
    attrs = models.CharField(
        _('attributes'), max_length=1024,
        blank=True, null=True
    )
    parent = models.ForeignKey(
        'self', blank=True, null=True,
        related_name='children'
    )
    url = models.CharField(
        _("URL"), max_length=256, blank=True, null=True
    )
    is_url = models.BooleanField(
        _('is url?'), default=True
    )
    is_hidden = models.BooleanField(
        _("is hidden"),
        help_text=_("marks menu item as hidden"),
        default=False)

    def __str__(self):
        out = self.title
        target = self
        while 1:
            if target.parent is None:
                break
            out = target.parent.title + '->' + out
            target = target.parent
        return out

    def get_url(self):
        return self.url

    def get_absolute_url(self):
        return self.url

    def get_children(self, is_hidden=False):
        return self.children.filter(is_hidden=is_hidden)

    @property
    def has_children(self, is_hidden=False):
        return bool(self.get_children(is_hidden))

    class Meta:
        verbose_name = _("Vertical Menu")
        verbose_name_plural = _("Vertical Menus")
        ordering = ['is_url', 'order', 'id']

from apps.menu.signals import setup_signals
setup_signals()
