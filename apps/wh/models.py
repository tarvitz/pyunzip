# coding: utf-8

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group

from django.contrib.contenttypes import generic
from django.conf import settings
from django.core.urlresolvers import reverse

from datetime import datetime
from apps.core.helpers import post_markup_filter, render_filter


class Universe(models.Model):
    codename = models.CharField(
        _('сodename'), max_length=100, unique=True,
        primary_key=True
    )
    title = models.CharField(
        _('title'), max_length=100)

    def __unicode__(self):
        return self.codename


class Fraction(models.Model):
    title = models.CharField(
        _('fraction'), max_length=30, null=False)
    universe = models.ForeignKey(
        Universe, blank=True, null=True
    )

    def __unicode__(self):
        return self.title


class Side(models.Model):
    name = models.CharField(
        _('side'), max_length=40, null=False
    )
    fraction = models.ForeignKey(Fraction)

    def __unicode__(self):
        return self.name


class Army(models.Model):
    name = models.CharField(
        _('army'), max_length=100,
        null=False
    )
    side = models.ForeignKey(Side)

    def __unicode__(self):
        return "[%s]:%s" % (self.side.name, self.name)

    @property
    def get_side_name(self):
        return self.side.name.replace(' ', '_').lower()

    class Meta:
        verbose_name = _('Army')
        verbose_name_plural = _('Armies')
        ordering = ['side', ]


class MiniQuote(models.Model):
    content = models.CharField(
        _('content'), max_length=255
    )

    def __unicode__(self):
        return self.content

    class Meta:
        verbose_name = _('Mini Quote')
        verbose_name_plural = _('Mini Quotes')


class Expression(models.Model):
    author = models.CharField(
        _('author'), max_length=100, blank=True
    )
    original_content = models.TextField(
        _('original'),
        help_text=_('Original text of expression'),
        max_length=500, blank=True
    )
    content = models.TextField(
        _('translation'),
        help_text=_('translation of original sentence'),
        max_length=500, blank=True
    )
    fraction = models.ForeignKey(Fraction)

    def show_original_content(self):
        num = 50
        if self.original_content:
            if len(self.original_content) > num:
                return self.original_content[0:num] + " ..."
            else:
                return self.original_content[0:num]
        return ''
    show_original_content.short_description = _('original content')

    def show_content(self):
        num = 50
        if self.content:
            if len(self.content) > num:
                return self.content[0:num] + " ..."
            else:
                return self.content[0:num]
        return ''
    show_content.short_description = _('content')

    def show_author(self):
        num = 20
        if self.author:
            if len(self.author) > num:
                return self.author[0:num] + " ..."
            else:
                return self.author[0:num]
        return ''
    show_author.short_description = _('author')

    def __unicode__(self):
        if self.original_content:
            return self.original_content
        elif self.content:
            return self.content
        return ''

    class Meta:
        ordering = ['id']
        verbose_name = _('expression')
        verbose_name_plural = _('expressions')


class PM(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='sender',
        verbose_name=_("sender")
    )
    addressee = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='addressee',
        verbose_name=_("addressee")
    )
    title = models.CharField(
        _('title'), max_length=50
    )
    content = models.TextField(_('text'))
    cache_content = models.TextField(
        _("cache content"), blank=True, null=True
    )
    is_read = models.BooleanField(_('is read'), default=False)
    sent = models.DateTimeField(
        _('sent'), auto_now=True, default=datetime.now
    )
    dbs = models.BooleanField(_('deleted by sendr'), default=False)
    dba = models.BooleanField(_('deleted by addr'), default=False)
    syntax = models.CharField(
        _('syntax'), max_length=50,
        choices=settings.SYNTAX, blank=True, null=True
    )
    #TODO: Do we need files in PM ?

    class Meta:
        verbose_name = _('Private Message')
        verbose_name_plural = _('Private Messages')

    def purge_msg(self):
        if self.dbs and self.dba:
            self.remove()
        return

    def __unicode__(self):
        return self.title

    def render(self, field):
        return render_filter(
            post_markup_filter(getattr(self, field)),
            self.syntax
        )



# noinspection PyShadowingBuiltins
class RankType(models.Model):
    type = models.CharField(_('type'), max_length=100)
    magnitude = models.IntegerField(
        _('magnitude'), help_text=_('lower magnitude id more powerfull')
    )
    style = models.TextField(
        _('CSS Style'), max_length=1024, null=True, blank=True)
    css_class = models.CharField(
        _('CSS class'), max_length=64, null=True, blank=True)
    css_id = models.CharField(_('CSS id'), max_length=64, null=True,
                              blank=True)
    group = models.ForeignKey(Group, null=True, blank=True)

    def __unicode__(self):
        return self.type


# noinspection PyShadowingBuiltins
class Rank(models.Model):
    short_name = models.CharField(_('short name'), max_length=50)
    codename = models.CharField(
        _('codename'), max_length=100, unique=True
    )
    type = models.ForeignKey(RankType, null=True, blank=True)
    description = models.TextField(_('description'))
    magnitude = models.IntegerField(
        _('magnitude'), help_text=_('Lower magnitude more powerfull'),
        blank=True, null=True
    )
    side = models.ManyToManyField(Side, blank=True)
    is_general = models.BooleanField(_('is General'), blank=True,
                                     default=False)
    syntax = models.CharField(
        _('syntax'), max_length=50, choices=settings.SYNTAX,
        blank=True, null=True
    )

    def __unicode__(self):
        if self.type is not None:
            return "%s:%s" % (self.type.type, self.short_name)
        return self.short_name

    def _get_name(self):
        return self.short_name

    name = property(_get_name)

    get_style = lambda self: self.type.style
    get_css_class = lambda self: self.type.css_class
    get_css_id = lambda self: self.type.css_id

    def get_absolute_url(self):
        return reverse('wh:rank', args=(self.id,))

    class Meta:
        verbose_name = _("Rank")
        verbose_name_plural = _("Ranks")


class AbstractActivity(models.Model):
    activity_date = models.DateTimeField(
        _('dateTime activity'), blank=False, null=True
    )
    activity_ip = models.IPAddressField(_('IP address'))

    class Meta:
        abstract = True


class UserActivity(AbstractActivity):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
    is_logout = models.NullBooleanField(_('is logout'))
    last_action_time = models.DateTimeField(
        _('Last action time'),
        null=True, blank=True
    )

    def show_nickname(self):
        return self.user.nickname
    show_nickname.short_description = _('User')

    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')


class WarningType(models.Model):
    codename = models.CharField(
        _('codename'), max_length=30, unique=True
    )
    description = models.CharField(
        _('description'), max_length=200
    )
    level = models.IntegerField(
        _('level')
    )
    side = models.ManyToManyField(Side, blank=True)
    is_general = models.BooleanField(
        _('is general'), blank=True, default=False
    )

    class Meta:
        pass

    def __unicode__(self):
        return self.description


# noinspection PyShadowingBuiltins
class Warning(models.Model):
    style = models.CharField(_('style'), max_length=200)
    type = models.ForeignKey(WarningType)
    level = models.IntegerField(
        _('sign'), max_length=10, choices=settings.SIGN_CHOICES
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, primary_key=True)
    expired = models.DateTimeField(_('expired'))
    comments = generic.GenericRelation(
        'comments.Comment', object_id_field='object_pk'
    )

    def _get_sign(self):
        return settings.SIGN_CHOICES[int(self.level)-1][1]
    sign = property(_get_sign)

    def __unicode__(self):
        return self.user.nickname

    class Meta:
        permissions = (
            (u'set_warnings', _('Can set warnings')),
        )

    def show_nickname(self):
        return self.user.nickname
    show_nickname.short_description = _('User')


from apps.wh.signals import setup_signals
setup_signals()
