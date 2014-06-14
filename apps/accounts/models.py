# coding: utf-8
import re
import os

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, UserManager, PermissionsMixin)

from picklefield import PickledObjectField
from django.db.models import Sum
from django.core import validators
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta
import logging
logger = logging.getLogger(__name__)

# Create your models here.
GENDER_CHOICES = (
    ('m', _('male')),
    ('f', _('female')),
    ('n', _('not identified'))
)

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
    army = models.ForeignKey('wh.Army', null=True, blank=True,
                             verbose_name=_("army"))

    gender = models.CharField(
        _('gender'), default='n', max_length=1,
        choices=GENDER_CHOICES
    )
    jid = models.EmailField(_('jabber id'), max_length=255,
                            blank=True, null=True)

    uin = models.IntegerField(_('uin (icq number)'), max_length=12,
                              blank=True, null=True, default=0)
    about = models.CharField(_('about myself'), max_length=512, blank=True,
                             null=True)
    tz = models.FloatField(_('time zone'), choices=TZ_CHOICES, default=0)
    settings = PickledObjectField(_('Settings'), null=True, blank=True)
    # extensions
    karma = models.IntegerField(
        _('karma'), default=0, help_text=_("user's karma"), null=True,
        blank=True
    )
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
            'accounts:profile-by-nick', args=(
                self.nickname or self.username, )
        )

    @staticmethod
    def get_profile_url():
        return reverse('accounts:profile')

    @staticmethod
    def get_update_profile_url():
        return reverse('accounts:profile-update')

    @staticmethod
    def get_password_change_url():
        return reverse('accounts:password-change')

    @staticmethod
    def get_pm_inbox_url():
        return reverse('accounts:pm-inbox')

    @staticmethod
    def get_pm_outbox_url():
        return reverse('accounts:pm-outbox')

    def get_policy_warnings_url(self):
        return reverse('accounts:warning-list', args=(self.pk, ))

    def get_policy_warning_create_url(self):
        return reverse('accounts:warning-create', args=(self.pk, ))

    def get_karma_url(self):
        return reverse('karma:karma-list', args=(self.pk, ))

    def get_karma_up_url(self):
        return reverse('karma:karma-alter', args=('up', self.nickname))

    def get_karma_down_url(self):
        return reverse('karma:karma-alter', args=('down', self.nickname))

    def get_policy_warnings(self):
        return self.warning_user_set.filter(
            is_expired=False)

    def get_active_read_only_policy_warnings(self):
        return self.warnings.filter(level=settings.READONLY_LEVEL)

    @property
    def warnings(self):
        return self.get_policy_warnings()

    def get_color_theme(self):
        return self.get_forum_theme()

    def get_css_theme(self):
        return (self.settings or {'blank': True}).get('css_theme', 'light')

    def get_username(self):
        return self.nickname or self.username

    def get_gender(self):
        idx = [self.gender in i[0] for i in GENDER_CHOICES].index(True)
        return GENDER_CHOICES[idx][1]

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
                cache.set('nick:%s' % self.username, self.nickname or
                          self.username)
            return self.nickname or self.username
        return nickname

    def get_comments_count(self):
        from apps.comments.models import Comment
        return Comment.objects.filter(user=self).count()

    def get_karma_value(self):
        amount = self.karma_user_set.aggregate(Sum('value'))
        amount = amount.items()[0][1] or 0
        return amount

    def get_unwatched_events(self):
        from apps.news.models import Event, EventWatch
        time_offset = datetime.now() - timedelta(days=31)
        exclude_qs = EventWatch.objects.filter(created_on__gte=time_offset,
                                               user=self)
        self._unwatched_events = Event.objects.filter(
            is_finished=False).exclude(event_watch_set=exclude_qs)
        return self._unwatched_events

    def get_new_pm(self):
        return self.addressee.filter(is_read=False, dba=False)

    def get_forum_theme(self):
        if isinstance(self.settings, dict):
            return self.settings.get('forum_theme',
                                     settings.FORUM_THEME_DEFAULT)
        else:
            return settings.FORUM_THEME_DEFAULT

    @property
    def files(self):
        return self.user_file_set

    def __unicode__(self):
        return self.nickname or self.username

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")


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
        choices=settings.SYNTAX, blank=True, null=True,
        default=settings.DEFAULT_SYNTAX
    )

    class Meta:
        ordering = ['-sent', ]
        verbose_name = _('Private Message')
        verbose_name_plural = _('Private Messages')

    def purge_msg(self):
        if self.dbs and self.dba:
            self.remove()
        return

    def __unicode__(self):
        return self.title

    def render(self, field):
        from apps.core.helpers import render_filter, post_markup_filter
        return render_filter(
            post_markup_filter(getattr(self, field)),
            self.syntax
        )

    # urls
    def get_absolute_url(self):
        return reverse('accounts:pm-detail', args=(self.pk, ))

    @staticmethod
    def get_delete_url():
        return ''

    def get_reply_url(self):
        return reverse('accounts:pm-reply', args=(self.pk, ))


POLICY_WARNING_LEVEL_CHOICES = (
    (1, "*"),
    (2, "**"),
    (3, "+"),
    (4, "++"),
    (settings.READONLY_LEVEL, _("read only")),
    #(6, _('ban')),
    #(7, _('perm ban'))
)


class PolicyWarning(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='warning_user_set',
        verbose_name=_('user')
    )
    comment = models.CharField(_('comment'), max_length=4096,
                               blank=True, null=True)
    level = models.PositiveIntegerField(_("level"), default=1,
                                        choices=POLICY_WARNING_LEVEL_CHOICES)
    created_on = models.DateTimeField(_("created on"), auto_now_add=True,
                                      default=datetime.now)
    updated_on = models.DateTimeField(_("updated on"), default=datetime.now)
    date_expired = models.DateField(
        _('date expired'), default=datetime.now,
        help_text=_("date then warning is expired")
    )
    is_expired = models.BooleanField(
        _('is expired'), default=False,
        help_text=_("marks if warning is expired for this user")
    )

    # urls
    def get_absolute_url(self):
        return reverse('accounts:warning-detail', args=(self.pk, ))

    def get_edit_url(self):
        return reverse('accounts:warning-update', args=(self.pk, ))

    def get_delete_url(self):
        return reverse('accounts:warning-delete', args=(self.pk, ))

    # methods
    def get_level(self):
        """gets human friendly policy level for current user instance

        :return: human friendly policy warning level
        :rtype: str
        """
        idx = [
            self.level in i for i in POLICY_WARNING_LEVEL_CHOICES].index(True)
        return POLICY_WARNING_LEVEL_CHOICES[idx][1]

    def __unicode__(self):
        return '[%(level)s] %(date)s' % {
            'level': self.get_level(),
            'date': self.date_expired.strftime('%d-%m-%Y')
        }

    class Meta:
        ordering = ['-date_expired', ]
        verbose_name = _("Policy warning")
        verbose_name_plural = _("Policy warnings")


from apps.accounts import signals
signals.setup_run()
