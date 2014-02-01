# coding: utf-8

import os

from django.db import models
from django.db.models import Q, Sum
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, Group
from django.contrib.comments.models import Comment

from django.contrib.contenttypes import generic

from apps.core.helpers import safe_ret
from picklefield import PickledObjectField
from django.core.urlresolvers import reverse
from apps.djangosphinx.models import SphinxSearch
from django.core.cache import cache
from datetime import datetime
from apps.core.helpers import post_markup_filter, render_filter


class Universe(models.Model):
    codename = models.CharField(
        _('сodename'), max_length=100, unique=True, primary_key=True
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
        User, related_name='sender',
        verbose_name=_("sender")
    )
    addressee = models.ForeignKey(
        User, related_name='addressee',
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

class RegisterSid(models.Model):
    sid = models.CharField(
        _('SID'),
        max_length=40, primary_key=True
    )
    ip = models.CharField(_('IP'), max_length=16)
    value = models.CharField(_('value'), max_length=10)
    expired = models.DateTimeField(_('expired'))

    class Meta:
        verbose_name = _("RegisterSID")
        verbose_name_plural = _("RegisterSIDs")


class Skin(models.Model):
    name = models.CharField(_('name'), max_length=40)
    description = models.TextField(_('description'))
    fraction = models.ManyToManyField(Fraction, blank=True)
    is_general = models.BooleanField(_('is general'), blank=True, default=False)

    def __unicode__(self):
        return self.name.lower()

    def __repr__(self):
        return self.name.lower()


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
    css_id = models.CharField(_('CSS id'), max_length=64, null=True, blank=True)
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
    is_general = models.BooleanField(_('is General'), blank=True, default=False)
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
    user = models.OneToOneField(User, primary_key=True)
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


class GuestActivity(AbstractActivity):
    activity_date_prev = models.DateTimeField(
        _('prev datetime activity'), blank=True, null=True
    )

    class Meta:
        verbose_name = _('Guest Activity')
        verbose_name_plural = _('Guest Activities')


class Settings(models.Model):
    class Meta:
        abstract = True


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
    type  = models.ForeignKey(WarningType)
    level = models.IntegerField(
        _('sign'), max_length=10, choices=settings.SIGN_CHOICES
    )
    user = models.ForeignKey(User, primary_key=True)
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


class IPBan(models.Model):
    ip_address = models.IPAddressField(_('ip address'))
    description = models.CharField(_('description'))
    user = models.ForeignKey(User)

    class Meta:
        abstract = True


class RangeIPBan(models.Model):
    ip_range = models.IPAddressField(_('ip range address'))

    class Meta:
        abstract = True


TZ_CHOICES = [(float(x[0]), x[1]) for x in (
    (-12, '-12'), (-11, '-11'), (-10, '-10'), (-9.5, '-09.5'), (-9, '-09'),
    (-8.5, '-08.5'), (-8, '-08 PST'), (-7, '-07 MST'), (-6, '-06 CST'),
    (-5, '-05 EST'), (-4, '-04 AST'), (-3.5, '-03.5'), (-3, '-03 ADT'),
    (-2, '-02'), (-1, '-01'), (0, '00 GMT'), (1, '+01 CET'), (2, '+02'),
    (3, '+03'), (3.5, '+03.5'), (4, '+04'), (4.5, '+04.5'), (5, '+05'),
    (5.5, '+05.5'), (6, '+06'), (6.5, '+06.5'), (7, '+07'), (8, '+08'),
    (9, '+09'), (9.5, '+09.5'), (10, '+10'), (10.5, '+10.5'), (11, '+11'),
    (11.5, '+11.5'), (12, '+12'), (13, '+13'), (14, '+14'),
)]


#monkey patching

User.__unicode__ = lambda x: x.nickname or x.username
User.add_to_class(
    'nickname',
    models.CharField(
        _('nickname'), max_length=30, null=False, unique=True, default=None
    )
)
User.add_to_class(
    'photo', models.ImageField(
        _('photo'), upload_to=os.path.join(
            settings.MEDIA_ROOT + 'photos/'
        ),
        blank=True
    )
)
User.add_to_class(
    'avatar', models.ImageField(
        _('Avatar'), upload_to=os.path.join(
            settings.MEDIA_ROOT + 'avatars/'
        ),
        blank=True)
)
User.add_to_class(
    'plain_avatar', models.ImageField(
        _('plain Avatar'), upload_to=os.path.join(
            settings.MEDIA_ROOT + 'avatars/'),
        blank=True
    )
)
User.add_to_class(
    'gender', models.CharField(
        _('gender'), default='n', max_length=1,
        choices=[
            ('m', _('male')),
            ('f', _('female')),
            ('n', _('not identified'))
        ]
    )
)
User.add_to_class(
    'jid', models.CharField(
        _('jabber id'), max_length=255, blank=True, null=True)
)
User.add_to_class(
    'uin', models.IntegerField(
        _('uin (icq number)'), max_length=12, blank=True, null=True)
)
User.add_to_class(
    'about', models.CharField(
        _('about myself'), max_length=512, blank=True)
)
User.add_to_class(
    'skin', models.ForeignKey(
        Skin, null=True, blank=True)
)
User.add_to_class(
    'ranks',
    models.ManyToManyField(Rank, null=True, blank=True)
)
User.add_to_class(
    'army', models.ForeignKey(Army, null=True, blank=True)
)
User.add_to_class(
    'tz', models.FloatField(
        _('time zone'), choices=TZ_CHOICES, default=0)
)
User.add_to_class(
    'settings', PickledObjectField(_('Settings'), null=True, blank=True)
)
Comment.add_to_class(
    'syntax', models.CharField(
        _('Syntax'), max_length=50, null=True, blank=True,
        choices=settings.SYNTAX)
)
Comment.add_to_class('search', SphinxSearch(weights={'comment': 100}))
Comment.add_to_class(
    'cache_comment', models.TextField(
        _("cache comment"), null=True, blank=True
    )
)


# UserAdmin import should be placed heres
from django.contrib.auth.admin import UserAdmin
UserAdmin.raw_id_fields += ('ranks',)
UserAdmin.fieldsets += (
    (
        _('Profile'),
        {
            'fields': (
                'nickname', 'photo', 'avatar', 'plain_avatar', 'army',
                'gender', 'jid', 'uin', 'about', 'skin', 'ranks', 'tz'
            ),
            #'list_display': (
            #   'nickname', 'photo', 'avatar', 'army', 'gender',
            #   'jid', 'uin', 'about', 'skin'
            # )
        }
    ),
)
creation_fields = ('username', 'nickname', 'password1', 'password2')
UserAdmin.add_fieldsets[0][1]['fields'] = creation_fields
from django.contrib.comments.admin import CommentsAdmin
CommentsAdmin.fieldsets += (
    (
        _('Overload'),
        {
            'fields': ('syntax',)
        }
    )
)


# noinspection PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyShadowingBuiltins
class UserExtension(object):
    @property
    def files(self):
        return self.user_file_set

    def get_absolute_url(self):
        return reverse(
            'wh:profile-by-nick', args=(
                self.nickname or self.username, )
        )

    def __repr__(self):
        return '<User: %s>' % (self.nickname or self.username)

    def __unicode__(self):
        return self.nickname or self.username

    def get_avatar_url(self):
        avatar = None
        real_avatar = safe_ret(self, 'avatar.url') or ''
        if not real_avatar:
            avatar = os.path.join(settings.MEDIA_URL, 'avatars/none.png')
        avatar = avatar or real_avatar
        return avatar

    def get_username(self):
        return self.nickname or self.username

    def get_nickname(self, no_cache=False):
        nickname = (
            cache.get('nick:%s' % self.username)
            if not no_cache else None
        )
        if not nickname:
            if self.ranks.all():
                rank = self.ranks.order_by('-magnitude')[0]
                span = (
                    "<span class='%(class)s' id='%(id)s' "
                    "style='%(style)s'>%(nickname)s</span>" % {
                        'class': rank.type.css_class,
                        'id': rank.type.css_id,
                        'style': rank.type.style,
                        'nickname': self.nickname or self.username
                    }
                )
                if not no_cache:
                    cache.set('nick:%s' % self.username, span)
                return span
            if not no_cache:
                cache.set('nick:%s' % self.username, self.nickname or self.username)
            return self.nickname or self.username
        return nickname

    def get_ranks_groups(self):
        tuple = list()
        for rank in self.ranks.distinct():
            if rank.type.group:
                tuple.append(rank.type.group)
        return tuple

    def get_fraction(self):
        return self.army.side.fraction.title

    def get_comments_count(self):
        return Comment.objects.filter(user=self).count()

    def get_replays_count(self):
        return self.replay_set.count()

    def get_karma_value(self):
        amount = self.karma_owner_set.aggregate(Sum('value'))
        amount = amount.items()[0][1] or 0
        return amount

    @property
    def karma(self):
        return self.get_karma_value()

    def get_karma_status(self):
        # returns a karma status instance
        from apps.karma.models import KarmaStatus
        config = self.settings or {}
        is_humor = config.get('karma_humor', False)
        qset = Q(is_general=True)
        order_by = ['-value', ] if self.karma > 0 else ['value', ]
        kw = dict()

        if self.karma > 0:
            kw.update({'value__lte': int(self.karma)})
        else:
            kw.update({'value__gte': int(self.karma)})

        if is_humor:
            order_by += ['is_humor', ]
        if safe_ret(self, 'army.side'):
            qset = qset | Q(side=self.army.side)

        status = KarmaStatus.objects.order_by(*order_by).filter(
            Q(**kw) & qset
        )
        return status[0] if len(status) else None

    def get_magnitude(self):
        if self.is_superuser:
            return 0

        if not self.ranks:
            return 1000000  # extreamly high magnitude

        mag = 100000000
        for r in self.ranks.distinct():
            if r.type.magnitude < mag:
                mag = r.type.magnitude
        return mag

    def get_forum_theme(self):
        if isinstance(self.settings, dict):
            return self.settings.get('forum_theme',
                                     settings.FORUM_THEME_DEFAULT)
        else:
            return settings.FORUM_THEME_DEFAULT

    def get_private_forums(self):
        pass

    class Meta:
        permissions = (
            ('can_test', 'Can test functional')
        )


# noinspection PyUnresolvedReferences
class CommentExtension(object):
    def render_comment(self):
        """ renturns comment in render"""
        return render_filter(post_markup_filter(self.comment), self.syntax or 'textile')

    def get_content(self):
        return self.comment

    def get_title(self):
        if len(self.comment) > 100:
            return "%s ..." % self.comment[0:100]
        else:
            return self.comment

#class UserProfile(object):
    #def _get_comments(self):
    #    return Comment.object.get(user=self,
    #        is_public=True)
    #public_comments = property(_get_comments)
    #del _get_comments
    #
    #def _show_user(self):
    #    return self.username
    #show_user = _show_user
    #del _show_user
#    def __unicode__(self):
#        return self.username
#
#    class Meta:
#        permissions = USERPERMS
#
#May conflict with apache =\
#User.__bases__      = User.__bases__ + (UserExtension,)
# THIS IS BRAINS SCREW DO NOT REPEAT IT IN YOUR HOME
User.__bases__ = (UserExtension,) + User.__bases__
#User.__bases__     = User.__bases__ + (UserProfile,)
Comment.__bases__ = Comment.__bases__ + (CommentExtension,)
from apps.wh.signals import setup_signals
setup_signals()
