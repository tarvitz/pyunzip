from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext as tr
from apps.files.models import Attachment
from django.core.urlresolvers import reverse
from utils.models import copy_fields
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from apps.wh.models import Side
from apps.djangosphinx.models import SphinxSearch
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.core.exceptions import ValidationError
from apps.core.actions import common_delete_action
from apps.tabletop.actions import alter_codex_action

MODEL_UNIT_TYPE_CHOICES = (
    ('hq', _("hq")),
    ('troops', _("troops")),
    ('elite', _('elite')),
    ('fast', _('fast')),
    ('heavy support', _('heavy support')),
)

class Codex(models.Model):
    content_type = models.ForeignKey(ContentType,
        verbose_name=_('content type'),
        related_name="ct_set_for_%(class)s")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content type",
        fk_field="object_id")
    title = models.CharField(_('Title'), max_length=128)
    plain_side = models.CharField(_('Plain side'), max_length=128, blank=True) #for sphinx search optimization
    revisions = models.CommaSeparatedIntegerField(_('Revisions'), max_length=64)
    
    def bound(self):
        try:
            return self.content_type.model_class().objects.get(pk=self.object_id)
        except:
            return None

    def __unicode__(self):
        return self.bound().__unicode__()
    
    def save(self, *args, **kwargs):
        #write plain_side for better search withing sphinx
        bound = self.bound()
        if bound:
            bound_name = bound.__class__.__name__.lower()
            if 'army' in bound_name:
                self.plain_side = bound.side.name
            else:
                self.plain_side = bound.name
        super(Codex, self).save(*args, **kwargs)

class Roster(models.Model):
    def valid_revision(value):
        if not 0 < value < 15:
            raise ValidationError, tr('should be with range of 0 to 100')
        return value
    owner = models.ForeignKey(User,related_name='roster_owner')
    title = models.CharField(_('Title'),max_length=100)
    user = models.ForeignKey(User,blank=True,null=True,related_name='user')
    player = models.CharField(_('Player'),blank=True,max_length=32)
    roster = models.TextField(_('Roster'),max_length=4096)
    #may cause an errors as CharField was moved to TextField without database
    #changes
    comments = models.TextField(_('Comments'),max_length=10240,blank=True,null=True)
    #race = models.ForeignKey(Side,related_name='race',blank=True,null=True)
    codex = models.ForeignKey(Codex, blank=True, null=True, default=1)
    custom_codex = models.CharField(_('Custom Codex'),max_length=50,blank=True,null=True)
    revision = models.IntegerField(_('Revision'), validators=[valid_revision,])
    pts = models.IntegerField(_('pts')) #we should make A LOT OF CHECK UPS :( within
    syntax = models.CharField(_('Syntax'), max_length=20,blank=True,null=True,choices=settings.SYNTAX)

    is_orphan = models.NullBooleanField(_('Orphan'),default=False,blank=True,null=True) 
    search = SphinxSearch(weights={'title': 30, 'comments': 30})
    actions = [common_delete_action, alter_codex_action]

    def show_player(self):
       if hasattr(self.user,'nickname'): return self.user.get_username
       if self.player: return self.player
       if self.owner: return self.owner.get_username
    show_player.short_description = _('Player')

    def get_title(self):
        return self.title

    def __unicode__(self):
        player_name = self.show_player()
        codex = self.codex.bound()
        return "%s [%s:%s:%i] [%i]" % (self.title, player_name, codex, self.pts, self.revision)

    def save(self,*args,**kwargs):
        from apps.core.helpers import get_user
        if not self.player:
            self.user = self.owner
        else:
            user = get_user(nickname=self.player)
            if user:
                self.user = user
        super(Roster,self).save(*args,**kwargs)

    def get_absolute_url(self):
        return reverse('url_show_roster',args=[self.id])
    class Meta:
        permissions = (
            ('edit_anonymous_rosters','Can edit anonymous rosters'),
            ('edit_user_rosters','Can edit another user\'s rosters'),
        )
        ordering = ['-id']

class Game(models.Model):
    name = models.CharField(_('Title'),primary_key=True,max_length=50)
    codename = models.CharField(_('Codename'),max_length=15,unique=True)

    def __unicode__(self):
        return self.name
    class Meta:
        pass
        #abstract = True

class Mission(models.Model):
    title = models.CharField(_('Title'),max_length=50)
    game = models.ForeignKey(Game)

    def __unicode__(self):
            return self.title
    class Meta:
        pass
        
class BattleReport(models.Model):
    title = models.CharField(_('Title'),max_length=100)
    owner = models.ForeignKey(User,related_name=_('Owner'))
    published = models.DateTimeField(_('Published'))
    #boo :) 
    users = models.ManyToManyField(Roster, verbose_name=_('Rosters'))
    winner = models.ForeignKey(Roster,related_name='winner',
        blank=True, null=True)
    mission = models.ForeignKey(Mission)
    layout = models.CharField(_('Layout'),max_length=30)
    comment = models.TextField(_('Comment'),max_length=10240)
    approved = models.BooleanField(_('Approved'),default=False,blank=True)
    ip_address = models.IPAddressField(_('IP address'),blank=True,null=True)
    syntax = models.CharField(_('Syntax'),max_length=20,choices=settings.SYNTAX)
    search = SphinxSearch(weights={'title': 30, 'comment': 30})
    actions = [common_delete_action, ]
    def __unicode__(self):
        return "%s [%s:%s]" % (
            self.title,
            self.mission.game.codename,
            self.mission.title
        )
    def get_absolute_url(self):
        return reverse('show_battle_report',args=[self.id,])
    def get_title(self):
        return self.title

    def delete(self,*args,**kwargs):
        """ deletes battlereport instance with rosters which already had been deleted
        (orphans)"""
        for r in self.users.distinct():
            if r.is_orphan: r.delete()
        super(BattleReport,self).delete(*args,**kwargs)

    def _get_general_pts(self):
        pts = self.users.distinct()[0].pts
        for r in self.users.all():
            if r.pts != pts:
                return _('[fuzzy] ')
        return self.users.distinct()[0].pts
    general_pts = property(_get_general_pts)
    
    def _get_versus_layout(self):
        """"""
        lst = list()
        pieces = self.layout.split('vs')
        for j in pieces:
            for k in xrange(0,int(j)):
                #print k,j
                if k == int(j)-1: lst.append(True)
                else: lst.append(False)
        #remove last item and replace it within False
        lst.pop(len(lst)-1)
        lst.append(False)
        return lst
        #print self.layout,':',lst
    bool_versus_layout = property(_get_versus_layout)
    
    #def _show_races(self):
    #    races = list()
    #    for r in self.users.distinct():
    #        races.append(r.race)
    #    return races
    #races = property(_show_races)

    def clean_rosters(self):
        for r in self.users.distinct():
            self.users.remove(r)
        self.save()

    class Meta:
        ordering = ['-id',]
        #permissions = (
        #)
        #abstract = True

class Army(models.Model):
    title = models.CharField(_("title"), max_length=256)
    __unicode__ = lambda s: s.title

    class Meta:
        verbose_name = _("Army")
        verbose_name_plural = _("Armies")

class Rule(models.Model):
    class Meta:
        abstract = True

class AutoRoster(models.Model):
    title = models.CharField(_('title'), max_length=256)
    army = models.ForeignKey(
        Army, related_name="auto_rosters"
    )
    description = models.CharField(
        _("description"), max_length=4096, blank=True, null=True
    )
    owner = models.ForeignKey(
        User, related_name='auto_roster_user_set'
    )
    pts = models.PositiveIntegerField(
        _("pts"), help_text=_("roster points cache"),
        default=0, blank=True, null=True
    )

    def __unicode__(self):
        return ("{owner}: {title}").format(
            owner=self.owner.nickname or self.owner.username,
            title=self.title
        )

    def reload_pts(self, rebuild=False, recursive=False):
        _pts = self.pts
        if recursive:
            for uc in self.unit_containers.all():
                uc.reload_pts(rebuild=rebuild)
                for wc in uc.wargear_containers.all():
                    wc.reload_pts(rebuild=rebuild)

        if not self.pts or rebuild:
            pts = sum([
                i['pts'] for i in self.unit_containers.values('pts')
            ])
            self.pts = pts
        if _pts != self.pts:
            self.save()
        return self

    class Meta:
        verbose_name = _("Auto roster")
        verbose_name_plural = _("Auto rosters")

class WargearContainer(models.Model):
    amount = models.PositiveIntegerField(
        _('amount'), help_text=_('wargear amount'),
    )
    pts = models.PositiveIntegerField(
        _('pts'), help_text=_("points cache for wargear"),
        blank=True, null=True, default=0
    )
    link = models.ForeignKey(
        'tabletop.Wargear', related_name='wargear_containers')
    unit = models.ForeignKey(
        'tabletop.UnitContainer', related_name='wargear_containers'
    )

    # stacks on UnitContainer
    def reload_pts(self, rebuild=False, commit=False):
        _pts = self.pts
        if not self.pts or rebuild:
            pts = (self.link.pts if self.link else 0) * self.amount
            self.pts = pts
        if _pts != self.pts and commit:
            self.save()
        return self

    def __unicode__(self):
        return ('[{id}] {model} + {gear} x{amount}, {roster}').format(
            id=self.id,
            model=self.unit.model_unit.title,
            roster=self.unit.roster.title,
            gear=self.link.title,
            amount=self.amount
        )

    class Meta:
        verbose_name = _("Wargear container")
        verbose_name_plural = _("Wargear containers")

class UnitContainer(models.Model):
    #includes wargear container
    amount = models.PositiveIntegerField(
        _('amount'), help_text=_('unit amount')
    )
    model_unit = models.ForeignKey(
        'tabletop.ModelUnit', related_name='units'
    )
    pts = models.PositiveIntegerField(
        _("pts"), help_text=_("points cache for unit"),
        blank=True, null=True, default=0
    )

    roster = models.ForeignKey(
        AutoRoster, related_name=_("unit_containers")
    )
    def reload_pts(self, rebuild=False, commit=False):
        _pts = self.pts
        if not self.pts or rebuild:
            pts = sum([
                i['pts'] for i in self.wargear_containers.values('pts')
            ])
            pts += (self.amount * self.model_unit.pts)
            self.pts = pts
        if _pts != self.pts and commit:
            self.save()
        return self

    def __unicode__(self):
        return ('[{id}] {model} x{amount} [{pts} pts], {roster}').format(
            id=self.id,
            model=self.model_unit.title,
            roster=self.roster.title,
            pts=self.pts or 0,
            amount=self.amount
        )
    class Meta:
        verbose_name = _("Unit container")
        verbose_name_plural = _("Unit containers")

class Unit(models.Model):
    class Meta:
        abstract = True

class ModelUnit(models.Model):
    type = models.CharField(
        choices=MODEL_UNIT_TYPE_CHOICES,
        default='hq', max_length=16
    )
    #ForeignKey(ModelUnitType, related_name='model_units')
    title = models.CharField(_('title'), max_length=256)
    description = models.CharField(
        _("description"), max_length=4096
    )
    army = models.ForeignKey(
        Army, related_name='model_units'
    )
    is_unique = models.BooleanField(
        _("is unique?"), help_text=_("marks if its unique"))
    pts = models.PositiveIntegerField(
        _('pts'), help_text=_("points per model unit"),
        default=0
    )
    min = models.PositiveIntegerField(
        _('min'), help_text=_("minumal models allowed be taken within squad"),
        default=1
    )
    max = models.PositiveIntegerField(
        _("max"), help_text=_("maximum models allowed be taken within squad"),
        default=1
    )
    mwr_amount = models.PositiveIntegerField(
        _('mwr amount'), help_text=_("must take wargear amount"),
        null=True, blank=True
    )
    
    def __unicode__(self):
        return ('{title} [{pts} - {type}]').format(
            title=self.title, pts=self.pts, type=self.type
        )

    class Meta:
        verbose_name = _("Model unit")
        verbose_name_plural = _("Model units")
        ordering = ('-id', )

class MWRUnit(models.Model):
    # model wargear requirement unit
    model_unit = models.ForeignKey(
        'tabletop.ModelUnit', related_name='requirements'
    )
    #amount = models.PositiveIntegerField(
    #    _("amount"), help_text=_("wargear amount requirements"),
    #    default=1
    #)
    wargear = models.ForeignKey(
        'tabletop.Wargear', related_name='mwr_requirements'
    )
    
    def __unicode__(self):
        return ('{unit} {wargear}').format(
            unit=self.model_unit.__unicode__(),
            wargear=self.wargear.title,
        )

    class Meta:
        verbose_name = _('MWRUnit')
        verbose_name_plural = _('MWRUnits')


class WargearRequirement(models.Model):
    # wargear requirement
    amount = models.PositiveIntegerField(
        _('amount'), help_text=_("requirement require amount"),
        default=1
    )
    amount_target = models.PositiveIntegerField(
        _('amount target'), help_text=_('wargear requirement target amount'),
        default=1
    )
    target = models.ForeignKey(
        'tabletop.Wargear',
        # for objects retrieve its requirements
        related_name='wargear_requirements'
    )
    require = models.ForeignKey(
        'tabletop.Wargear',
        # for objects retrieve its dependencies
        related_name='wargear_require_targets' 
    )
    
    def __unicode__(self):
        return ("[{amount_target}] {target}->{require} [{amount}]").format(
            amount_target=self.amount_target,
            target=self.target.title,
            require=self.require.title,
            amount=self.amount
        )

    class Meta:
        verbose_name = _("Wargear requirement")
        verbose_name_plural = _("Wargear requirements")

class Wargear(models.Model):
    title = models.CharField(_('title'), max_length=256)
    short_title = models.CharField(_("short title"), max_length=256, default='unkwn')
    description = models.CharField(_('description'), max_length=4096, blank=True)
    model_unit = models.ForeignKey(
        ModelUnit, related_name="wargear"
    )
    pts = models.PositiveIntegerField(
        _("pts"), help_text=_("points cost for one wargear title")
    )
    limit = models.PositiveIntegerField(
        _('limit'), help_text=_("limit gear to take on the battlefield"),
        default=1
    )
    is_squad_only = models.BooleanField(
        _('is squad only?'), help_text=_("marks if upgrade allowed for entire squad only"),
    )
    blocks = models.ManyToManyField(
        'self', help_text=_("marks what gear blocks given one"),
        related_name='blocked_by', blank=True
    )
    #depends = models.ManyToManyField(
    #    'self', help_text=_("depends on wargear"), blank=True
    #)

    def __unicode__(self):
        return ('{unit} {title}').format(
            unit=self.model_unit.title,
            title=self.title
        )

    def generate_short_title(self, commit=False):
        if not self.short_title:
            titles = [i['title'] for i in self.blocks.values('title')]
            short_titles = ["/".join(map(lambda x: x[0], titles)) for i in titles]
            self.short_title = short_titles
        if commit:
            self.save()
        return self

    class Meta:
        verbose_name = _("Wargear")
        verbose_name_plural = _("Wargears")


from apps.tabletop.signals import setup_signals
setup_signals()
