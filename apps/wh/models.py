# coding: utf-8

import os
import re

from django.db import models
from django.db.models import Q, Sum
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User,Group
from django.contrib.comments.models import Comment
#breaks model using via another apps
#from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes import generic
from apps.core.models import Settings as UserSettings
from picklefield import PickledObjectField
from django.core.urlresolvers import reverse
from apps.core.decorators import null
from apps.djangosphinx.models import SphinxSearch

class Universe(models.Model):
    codename = models.CharField(_('Codename'),max_length=100,unique=True,primary_key=True)
    title = models.CharField(_('Title'),max_length=100)
    def __unicode__(self):
        return self.codename

class Fraction(models.Model):
    title = models.CharField(_('Fraction'),max_length=30,null=False)
    universe = models.ForeignKey(Universe,blank=True,null=True)
    def __unicode__(self):
        return self.title

class Side(models.Model):
    name = models.CharField(_('Side'),max_length=40,null=False)
    fraction = models.ForeignKey(Fraction)

    def __unicode__(self):
        return self.name

class Army(models.Model):
    name = models.CharField(_('Army'), max_length=100, null=False)
    side = models.ForeignKey(Side)

    def __unicode__(self):
        return "[%s]:%s" % (self.side.name, self.name)

    @property
    def get_side_name(self):
        return self.side.name.replace(' ','_').lower()

    class Meta:
        verbose_name = _('Army')
        verbose_name_plural = _('Armies')
        ordering = ['side', ]

class MiniQuote(models.Model):
    content = models.CharField(_('Content'),max_length=255)

    class Meta:
        verbose_name = _('Mini Quote')
        verbose_name_plural = _('Mini Quotes')

class Expression(models.Model):
    author = models.CharField(_('Author'), max_length=100, blank=True)
    original_content = models.TextField(_('Original'), help_text=_('Original text of expression'), max_length=500, blank=True)
    content = models.TextField(_('Translation'), help_text=_('Translation of original sentence'),  max_length=500, blank=True)
    fraction = models.ForeignKey(Fraction)

    def show_original_content(self):
        num = 50
        if self.original_content:
            if len(self.original_content)>num: return self.original_content[0:num] + " ..."
            else: return self.original_content[0:num]
        return ''
    show_original_content.short_description = _('original content')
    def show_content(self):
        num = 50
        if self.content:
            if len(self.content)>num: return self.content[0:num] + " ..."
            else: return self.content[0:num]
        return ''
    show_content.short_description = _('content')

    def show_author(self):
        num = 20
        if self.author:
            if len(self.author)>num: return self.author[0:num] + " ..."
            else: return self.author[0:num]
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

class Profile(models.Model):
    #account = models.ForeignKey(User,unique=True)
    nickname = models.CharField(_('Nickname'),max_length=50,null=False,unique=True)
    photo = models.ImageField(_('Photo'),upload_to=os.path.join(settings.MEDIA_ROOT+'photos/'),blank=True)
    avatar = models.ImageField(_('Avatar'),upload_to=os.path.join(settings.MEDIA_ROOT+'avatars/'),help_text=_('Image must be 100x100 karge.'),blank=True)
    army = models.ForeignKey(Army)
    gender = models.CharField(_('Gender'),blank=True,default='n',max_length=1,choices=[('m','male'),('f','female'),('n','not identified')])
    jid = models.CharField(_('Jabber ID'),blank=True,max_length=255)
    uin = models.IntegerField(_('UIN (icq number'), max_length=12, blank=True)
    def __unicode__(self):
        if self.nickname: return self.nickname
        return ''

class PM(models.Model):
    sender = models.ForeignKey(User,related_name='sender')
    addressee = models.ForeignKey(User,related_name='addressee')
    title = models.CharField(_('Title'), max_length=50)
    content = models.TextField(_('Text'))
    is_read = models.BooleanField(_('Is read'))
    sent = models.DateTimeField(_('Sent'))
    dbs = models.BooleanField(_('Deleted by sendr'))
    dba = models.BooleanField(_('Delete by addr'))
    syntax = models.CharField(_('Syntax'),max_length=50,choices=settings.SYNTAX,blank=True,null=True)
    #TODO: Do we need files in PM ?
    #file = models.ForeignKey(_____)

    class Meta:
        verbose_name = _('Private Message')
        verbose_name_plural = _('Private Messages')
    def purge_msg(self):
        if self.dbs and self.dba:
            self.remove()
        return

class RegisterSid(models.Model):
    sid = models.CharField(_('SID'), max_length=40, primary_key=True)
    ip = models.CharField(_('IP'), max_length=16)
    value = models.CharField(_('Value'), max_length=10)
    expired = models.DateTimeField(_('Expired'))

class WishList(models.Model):
    anonymous = models.CharField(_('Name'), max_length=40, null=True, blank=True)
    author = models.ForeignKey(User)
    post = models.TextField(_('Post'))
    ip = models.CharField(_('IP'), max_length=16, null=True)
    published = models.BooleanField(_('Published'))
    approved = models.BooleanField(_('Approved'))

    class Meta:
        permissions = (
            ('can_approve', 'Can approve'),
            #('can_publish', _('Can publish')),
        )

class Skin(models.Model):
    name = models.CharField(_('Name'), max_length=40)
    description = models.TextField(_('Description'))
    #old
    #fraction = models.ForeignKey(Fraction)
    fraction = models.ManyToManyField(Fraction,blank=True)
    is_general = models.BooleanField(_('is General'),blank=True)
    def __unicode__(self):
        return self.name.lower()
    def __repr__(self):
        return self.name.lower()
    #def __str__(self):
    #    return self.name.lower()

class RankType(models.Model):
    type = models.CharField(_('Type'),max_length=100)
    magnitude = models.IntegerField(_('Magnitude'), help_text=_('Lower magnitude id more powerfull '))
    style = models.TextField(_('CSS Style'), max_length=1024, null=True,blank=True) # (#FF FF FF); gold, purple and so on
    css_class = models.CharField(_('CSS class'), max_length=64, null=True,blank=True)
    css_id = models.CharField(_('CSS id'),max_length=64, null=True,blank=True)
    group = models.ForeignKey(Group,null=True,blank=True)

    def __unicode__(self):
        return self.type

class Rank(models.Model):
    short_name = models.CharField(_('Short name'), max_length=50)
    codename = models.CharField(_('Codename'), max_length=100,unique=True)
    type = models.ForeignKey(RankType, null=True, blank=True)
    description = models.TextField(_('Description'))
    magnitude = models.IntegerField(_('Magnitude'),help_text=_('Lower magnitude more powerfull'),blank=True,null=True)
    #fraction = models.ForeignKey(Fraction,blank=True,null=True)
    side = models.ManyToManyField(Side,blank=True)
    is_general = models.BooleanField(_('is General'),blank=True)
    syntax = models.CharField(_('Syntax'),max_length=50,choices=settings.SYNTAX,blank=True,null=True)
    def __unicode__(self):
        if self.type is not None:
            return "%s:%s" % (self.type.type,self.short_name)
        return self.short_name
    def _get_name(self):
        return short_name
    name = property(_get_name)

    get_style = lambda self: self.type.style
    get_css_class = lambda self: self.type.css_class
    get_css_id = lambda self: self.type.css_id
    def get_absolute_url(self):
        return reverse('wh:rank', args=(self.id,))

class AbstractActivity(models.Model):
    activity_date = models.DateTimeField(_('DateTime activity'),blank=False,null=True)
    activity_ip = models.IPAddressField(_('IP address'))
    class Meta:
        abstract = True

class UserActivity(AbstractActivity):
    user = models.OneToOneField(User, primary_key=True)
    is_logout = models.NullBooleanField(_('is logout'))
    last_action_time = models.DateTimeField(_('Last action time'), null=True,blank=True)
    #activity_date = models.DateTimeField(_('DateTime activity'))
    #activity_ip = models.IPAddressField(_('IP address'))
    def show_nickname(self):
        return self.user.nickname

    show_nickname.short_description = _('User')
    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')

class GuestActivity(AbstractActivity):
    activity_date_prev = models.DateTimeField(_('Prev DateTime activity'), blank=True, null=True)
    #activity_ip = models.IPAddressField(_('IP address'))
    class Meta:
        verbose_name = _('Guest Activity')
        verbose_name_plural = _('Guest Activities')


class Settings(models.Model):
#    skin = models.ForeignKey(Skin)
    class Meta:
        abstract = True

    #def _get_links_template(self):
    #    return settings.LINKS_TEMPLATE
    #links_template = property(_get_links_template)
    #
    #def _get_comments_template(self):
    #    return settings.COMMENTS_TEMPLATE
    #comments_template = property(_get_comments_template)
    #
    #def _get_replay_inc_template(self):
    #    return settings.REPLAY_INC_TEMPLATE

class WarningType(models.Model):
    codename = models.CharField(_('Codename'),max_length=30,unique=True)
    description = models.CharField(_('Description'),max_length=200)
    level = models.IntegerField(_('Level'))
    side = models.ManyToManyField(Side,blank=True)
    is_general = models.BooleanField(_('Is general'),blank=True)

    class Meta:
        #abstract = True
        pass
    def __unicode__(self):
        return self.description

class Warning(models.Model):
    style = models.CharField(_('Style'), max_length=200)
    type  = models.ForeignKey(WarningType)
    level = models.IntegerField(_('Sign'),max_length=10,choices=settings.SIGN_CHOICES)
    user = models.ForeignKey(User,primary_key=True)
    #despite expired the should use OneToOne field relationship
    expired = models.DateTimeField(_('Expired'))
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

            (u'set_warnings','Can set warnings'),

        )
    def show_nickname(self):
        return self.user.nickname
    show_nickname.short_description = _('User')

class IPBan(models.Model):
    ip_address = models.IPAddressField(_('Ip Address'))
    description = models.CharField(_('Description'))
    user = models.ForeignKey(User)

    class Meta:
        abstract = True

#implement IPRangeAddressField
class RangeIPBan(models.Model):
    ip_range = models.IPAddressField(_('Ip Range Address'))
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

#is it dirty hack?
has_perm_vanilla = User.has_perm
def has_perm_overload(self,perm):
    ret = has_perm_vanilla(self,perm)
    if ret: return ret
    else:
        ranks = self.ranks.distinct()
        u_perms = list()
        for r in ranks:
            perms = r.type.group.permissions.distinct() #[0].content_type.name.lower()
            for p in perms:
                perms = "%s.%s" % (p.content_type.app_label.lower(),p.codename)
                u_perms.append(perms)
                #print perms
                if perm in perms:
                    return True
        if perm in u_perms: return True
        else:
            return False
vanilla_perms = User.get_all_permissions
def get_all_perms(self):
    perms = vanilla_perms(self)
    for r in self.ranks.distinct():
        for g in r.type.group.permissions.distinct():
            perm = "%s.%s" % (g.content_type.app_label,g.codename)
            perms.update([perm])
    return perms

#monkey patching
#User.has_perm = has_perm_overload
#User.get_all_permissions = get_all_perms
User.__unicode__ = lambda x: x.nickname or x.username #dirty cheat xD
User.add_to_class('nickname', models.CharField(_('Nickname'), max_length=30, null=False, unique=True, default=None))
User.add_to_class('photo', models.ImageField(_('Photo'),upload_to=os.path.join(settings.MEDIA_ROOT+'photos/'),blank=True))
User.add_to_class('avatar', models.ImageField(_('Avatar'),upload_to=os.path.join(settings.MEDIA_ROOT+'avatars/'),blank=True))
User.add_to_class('plain_avatar',models.ImageField(_('Plain Avatar'),upload_to=os.path.join(settings.MEDIA_ROOT+'avatars/'),blank=True))
User.add_to_class('gender', models.CharField(_('Gender'), default='n', max_length=1, choices=[('m',_('male')),('f',_('female')),('n',_('not identified'))]))
User.add_to_class('jid', models.CharField(_('Jabber ID'), max_length=255, blank=True, null=True))
User.add_to_class('uin', models.IntegerField(_('UIN (icq number)'), max_length=12, blank=True,null=True))
User.add_to_class('about', models.CharField(_('About myself'),max_length=512, blank=True))
User.add_to_class('skin', models.ForeignKey(Skin, null=True, blank=True))
User.add_to_class('ranks', models.ManyToManyField(Rank, null=True, blank=True))
User.add_to_class('army', models.ForeignKey(Army, null=True, blank=True))
User.add_to_class('tz', models.FloatField(_('Time zone'),choices=TZ_CHOICES, default=0))
User.add_to_class('settings', PickledObjectField(_('Settings'), null=True, blank=True))

#User.add_to_class('settings', models.ForeignKey(Settings))
#Comment
Comment.add_to_class('syntax',models.CharField(_('Syntax'),max_length=50,null=True,blank=True,choices=settings.SYNTAX))
Comment.add_to_class('search', SphinxSearch(weights={'comment': 100}))

#works here O_O
from django.contrib.auth.admin import UserAdmin
UserAdmin.raw_id_fields += ('ranks',)
UserAdmin.fieldsets += (
     (_('Profile'),

        {
            'fields': ('nickname','photo','avatar','plain_avatar','army','gender','jid','uin','about', 'skin', 'ranks','tz'),
        #'list_display': ('nickname','photo', 'avatar', 'army', 'gender', 'jid', 'uin', 'about', 'skin')
        }
     ),
    )
creation_fields = ('username', 'nickname', 'password1', 'password2')
UserAdmin.add_fieldsets[0][1]['fields'] = creation_fields
from django.contrib.comments.admin import CommentsAdmin
CommentsAdmin.fieldsets += (
    (_('Overload'),
        {
            'fields': ('syntax',)
        }
    ),
)
#USERPERMS = (
#    ('can_test', 'Can test functional'),
#)

# here is a bug?
class UserExtension(object):
    #properties
    @property
    def files(self):
        return self.user_file_set

    def get_absolute_url(self):
        return reverse('wh:profile-by-nick', args=(
            self.nickname or self.username,))

    def __repr__(self):
        return '<User: %s>' % (self.nickname or self.username)

    def __unicode__(self):
        return self.nickname or self.username

    def get_username(self):
        return self.nickname or self.username

    def _get_nickname(self):
        if self.is_superuser:
            return "<span style='color: #E37BC0;'>%s</span>" % \
                (self.nickname or self.username)
        if self.is_staff:
            return "<span style='color: gold;'>%s</span>" % \
                (self.nickname or self.username)
        #make here color implementation
        return self.nickname or self.username

    get_nickname = property(_get_nickname)
    def _get_ranks_groups(self):
        tuple = list()
        for rank in self.ranks.distinct():
            if rank.type.group:
                tuple.append(rank.type.group)
        return tuple

    get_ranks_groups = property(_get_ranks_groups)
    def _get_fraction(self):
        return self.army.side.fraction.title
    fraction = property(_get_fraction)

    def _get_comments_count(self):
        count = Comment.objects.filter(user=self).count()
        return count
    comments_count = property(_get_comments_count)

    def _get_replays_count(self):
        from apps.files.models import Replay
        count = Replay.objects.filter(author=self).count()
        return count
    replays_count = property(_get_replays_count)

    def get_karma_value(self):
        amount = self.karma_owner_set.aggregate(Sum('value'))
        amount = amount.items()[0][1] or 0
        return amount

    @property
    def karma(self):
        return self.get_karma_value()

    #obsolete
    """
    def _get_karma_value(self):
        from apps.karma.models import Karma
        raw = Karma.objects.filter(user=self)
        if len(raw)>0: count = raw[0].karma
        else: count = 0
        return count
    karma_value = property(_get_karma_value)
    """

    def get_magnitude(self):
        if self.is_superuser: return 0
	if not self.ranks:
            return 1000000 #extreamly high magnitude
        mag = 100000000
        for r in self.ranks.distinct():
            if r.type.magnitude<mag:
                mag = r.type.magnitude
        return mag

    class Meta:
        permissions = (
            ('can_test', 'Can test functional')
        )


class CommentExtension(object):
    def render_comment(self):
        """ renturns comment in render"""
        from apps.core.helpers import post_markup_filter as pmf, render_filter
        return render_filter(pmf(self.comment), self.syntax or 'textile')

    def get_content(self):
        return self.comment

    def get_title(self):
        if len(self.comment)>100:
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
