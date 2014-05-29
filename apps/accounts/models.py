# coding: utf-8
import re
import os

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, UserManager, PermissionsMixin)
from django.contrib.comments.models import Comment
from picklefield import PickledObjectField
from django.db.models import Q, Sum
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.core.urlresolvers import reverse

import logging
logger = logging.getLogger(__name__)

# Create your models here.


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


class User(PermissionsMixin, AbstractBaseUser):
    username = models.CharField(
        _('username'), max_length=40, unique=True,
        help_text=_('Required. 38 characters or fewer. Letters, numbers and '
                    '@/./+/-/_ characters'),
        validators=[
            validators.RegexValidator(re.compile('^[\w.@+-]+$'),
                                      _('Enter a valid username.'), 'invalid')
        ])
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into this admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether this user should be treated as '
                    'active. Unselect this instead of deleting accounts.')
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    # additional fields
    nickname = models.CharField(
        _('nickname'), max_length=32, unique=True,
        blank=True
    )
    avatar = models.ImageField(
        _('Avatar'), upload_to=(
            lambda x, fn: 'avatars/%i_%s' % (x.pk, fn)
        ),
        blank=True, null=True
    )
    plain_avatar = models.ImageField(
        _('plain Avatar'), upload_to=os.path.join(
            settings.MEDIA_ROOT + 'avatars/'),
        blank=True
    )
    photo = models.ImageField(
        _('photo'), upload_to=os.path.join(settings.MEDIA_ROOT + 'photos/'),
        blank=True
    )
    # TODO: refactor, redo, recode
    ranks = models.ManyToManyField('wh.Rank', null=True, blank=True)
    army = models.ForeignKey('wh.Army', null=True, blank=True)

    gender = models.CharField(
        _('gender'), default='n', max_length=1,
        choices=[
            ('m', _('male')),
            ('f', _('female')),
            ('n', _('not identified'))
        ]
    )
    jid = models.EmailField(_('jabber id'), max_length=255,
                            blank=True, null=True)

    uin = models.IntegerField(_('uin (icq number)'), max_length=12,
                              blank=True, null=True, default=0)
    about = models.CharField(_('about myself'), max_length=512, blank=True,
                             null=True)
    skin = models.ForeignKey('wh.Skin', null=True, blank=True)
    tz = models.FloatField(_('time zone'), choices=TZ_CHOICES, default=0)
    settings = PickledObjectField(_('Settings'), null=True, blank=True)
    # managers
    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', ]

    def get_full_name(self):
        if all([self.first_name, self.last_name]):
            return unicode(
                u'{first_name} {last_name}'.format(
                    first_name=self.first_name,
                    last_name=self.last_name
                )
            )
        return unicode(self.username)

    def get_short_name(self):
        if all([self.first_name, self.last_name]):
            return u'{first_name} {last_name}'.format(
                first_name=self.first_name,
                last_name=self.last_name
            )
        return self.username

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return settings.NULL_AVATAR_URL

    def get_absolute_url(self):
        return reverse(
            'wh:profile-by-nick', args=(
                self.nickname or self.username, )
        )

    def get_color_theme(self):
        return self.get_forum_theme()

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

    def get_comments_count(self):
        return Comment.objects.filter(user=self).count()

    def get_karma_value(self):
        amount = self.karma_owner_set.aggregate(Sum('value'))
        amount = amount.items()[0][1] or 0
        return amount

    @property
    def karma(self):
        return self.get_karma_value()

    def get_karma_status(self):
        from apps.core.helpers import safe_ret
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

    def get_forum_theme(self):
        if isinstance(self.settings, dict):
            return self.settings.get('forum_theme',
                                     settings.FORUM_THEME_DEFAULT)
        else:
            return settings.FORUM_THEME_DEFAULT

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

    @property
    def files(self):
        return  self.user_file_set

    def __unicode__(self):
        return self.nickname or self.username

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


from apps.accounts import signals
signals.setup_run()
