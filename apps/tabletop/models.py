# coding: utf-8
from django.db import models
from django.db.models import Min
from django.utils.translation import (
    ugettext_lazy as _, ugettext as tr,
    pgettext
)
from django.core.urlresolvers import reverse

from django.contrib.auth import get_user_model
User = get_user_model()

from django.conf import settings

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.core.exceptions import ValidationError

from apps.core.helpers import render_filter, post_markup_filter
from django.contrib.contenttypes import generic


MODEL_UNIT_TYPE_CHOICES = (
    ('hq', _("hq")),
    ('troops', _("troops")),
    ('elite', _('elite')),
    ('fast', _('fast')),
    ('heavy support', _('heavy support')),
)
MODEL_ARMY_TYPE_CHOICES = (
    ('infantry', _('infantry')),
    ('vehicle', _('vehicle')),
    ('bike', _("bike")),
    ('jetbike', _("jetbike")),
    ('flyer', _('flyer')),
    ('artilery', _("artilery")),
)

DEPLOYMENT_CHOICES = (
    ('dow', _("Dawn of War")),
    ('ha', _("Hammer and Anvil")),
    ('vs', _("Vanguard Strike")),
)


class Codex(models.Model):
    content_type = models.ForeignKey(ContentType,
                                     verbose_name=_('content type'),
                                     related_name="ct_set_for_%(class)s")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content type",
                                               fk_field="object_id")
    title = models.CharField(_('title'), max_length=128)
    #for sphinx search optimization
    plain_side = models.CharField(_('plain side'), max_length=128, blank=True)
    revisions = models.CommaSeparatedIntegerField(_('revisions'),
                                                  max_length=64)

    def bound(self):
        try:
            return self.content_type.model_class().objects.get(
                pk=self.object_id)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return u''

    def __unicode__(self):
        bound = self.bound()
        return bound.__unicode__() if bound else u''

    # noinspection PyUnresolvedReferences
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
            raise ValidationError(tr('should be with range of 0 to 100'))
        return value

    owner = models.ForeignKey(User, related_name='roster_owner')
    title = models.CharField(_('title'), max_length=100)
    user = models.ForeignKey(User, blank=True, null=True,
                             related_name='roster_user_set')
    player = models.CharField(_('player'), blank=True, max_length=32)
    roster = models.TextField(_('roster'), max_length=4096)

    comments = models.TextField(_('comments'), max_length=10240,
                                blank=True, null=True)

    codex = models.ForeignKey(
        Codex, blank=True, null=True, default=1,
        verbose_name=_("codex")
    )
    custom_codex = models.CharField(
        _('custom Codex'), max_length=50, blank=True, null=True
    )
    revision = models.IntegerField(
        #fixme: pgettext_lazy falls to exception within model form render :(
        pgettext('revision', 'codex revision'),
        validators=[valid_revision, ],
        help_text=_("revision means how new your codex is (bigger is newer)")
    )
    pts = models.IntegerField(
        _('pts'), help_text=_("amount of codex points")
    )
    syntax = models.CharField(_('Syntax'), max_length=20, blank=True,
                              null=True, choices=settings.SYNTAX)
    is_orphan = models.NullBooleanField(
        _('Orphan'), default=False, blank=True, null=True)
    wins = models.PositiveIntegerField(_('wins'), default=0, blank=True)
    defeats = models.PositiveIntegerField(_('defeats'), default=0, blank=True)

    def show_player(self):
        if hasattr(self.user, 'nickname'):
            return self.user.get_username()
        if self.player:
            return self.player
        if self.owner:
            return self.owner.get_username()
    show_player.short_description = _('Player')

    @property
    def won_reports(self):
        return self.breport_winners_sets

    @property
    def all_reports(self):
        return self.battlereport_set

    def reload_wins_defeats(self, save=True):
        common = self.all_reports.count()
        winned = self.won_reports.count()
        self.wins = winned
        self.defeats = common - winned
        if save:
            self.save()
        return self

    def get_title(self):
        return self.title

    def __unicode__(self):
        return u'%(title)s:%(pts)s' % {
            'title': self.title,
            'pts': self.pts
        }

    def save(self, *args, **kwargs):
        super(Roster, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tabletop:roster', args=(self.pk, ))

    def get_edit_url(self):
        return reverse('tabletop:roster-edit', args=(self.pk, ))

    def get_delete_url(self):
        return reverse('tabletop:roster-delete', args=(self.pk, ))
    #todo: SPEEDUP
    def render_roster(self):
        roster = post_markup_filter(self.roster)
        return render_filter(roster, self.syntax or 'textile')

    class Meta:
        permissions = (
            ('edit_anonymous_rosters', 'Can edit anonymous rosters'),
            ('edit_user_rosters', 'Can edit another user\'s rosters'),
        )
        ordering = ['-id']


class Game(models.Model):
    name = models.CharField(_('Title'), primary_key=True, max_length=50)
    codename = models.CharField(_('Codename'), max_length=15, unique=True)

    def __unicode__(self):
        return self.name

    class Meta:
        pass


class Mission(models.Model):
    title = models.CharField(_('Title'), max_length=50)
    game = models.ForeignKey(Game)

    def __unicode__(self):
            return self.title

    class Meta:
        pass


class BattleReport(models.Model):
    title = models.CharField(_('title'), max_length=100)
    owner = models.ForeignKey(User, related_name='battle_report_set')
    published = models.DateTimeField(
        _('published'), auto_now=True
    )
    #boo :)
    rosters = models.ManyToManyField(Roster, verbose_name=_('rosters'))
    winners = models.ManyToManyField(
        Roster,
        blank=True, null=True, verbose_name=_('winners'),
        related_name='breport_winners_sets'
    )
    mission = models.ForeignKey(Mission, verbose_name=_("mission"))
    layout = models.CharField(_('layout'), max_length=30)
    deployment = models.CharField(
        _('deployment'), choices=DEPLOYMENT_CHOICES, max_length=128,
        default='dow'
    )
    comment = models.TextField(_('comment'), max_length=10240)
    approved = models.BooleanField(_('approved'), default=False, blank=True)
    ip_address = models.IPAddressField(_('ip address'), blank=True, null=True)
    syntax = models.CharField(_('syntax'), max_length=20,
                              choices=settings.SYNTAX)

    def __unicode__(self):
        return "%s [%s:%s]" % (
            self.title,
            self.mission.game.codename,
            self.mission.title
        )

    def get_absolute_url(self):
        return reverse('tabletop:report', args=(self.id,))

    def get_title(self):
        return self.title

    def get_deployment(self):
        d = {}
        [d.update({i[0]: i[1]}) for i in DEPLOYMENT_CHOICES]
        return d[self.deployment]

    def delete(self, *args, **kwargs):
        # deletes battlereport instance with rosters which already
        # had been deleted
        # (orphans)
        for r in self.rosters.distinct():
            if r.is_orphan:
                r.delete()
        super(BattleReport, self).delete(*args, **kwargs)

    def get_approved_label(self):
        return 'success' if self.approved else 'inverse'

    def get_players(self):
        owners = [i.owner.pk for i in self.rosters.all()]
        return User.objects.filter(pk__in=owners).distinct()

    def _get_general_pts(self):
        pts = self.rosters.distinct()
        pts = pts[0] if len(pts) else None
        for r in self.rosters.all():
            if r.pts != pts:
                return _('[fuzzy] ')
        return pts
    general_pts = property(_get_general_pts)

    def get_pts(self):
        return self.rosters.all().aggregate(Min('pts')).items()[0][1]

    def get_head_content(self):
        if '(cut)' in self.comment:
            return post_markup_filter(
                render_filter(
                    self.comment[:self.comment.index('(cut)')],
                    self.syntax or 'textile'
                )
            )
        return post_markup_filter(
            render_filter(self.comment, self.syntax or 'textile')
        )

    def _get_versus_layout(self):
        """"""
        lst = list()
        pieces = self.layout.split('vs')
        for j in pieces:
            for k in xrange(0, int(j)):
                #print k,j
                if k == int(j)-1:
                    lst.append(True)
                else:
                    lst.append(False)
        #remove last item and replace it within False
        lst.pop(len(lst)-1)
        lst.append(False)
        return lst
    bool_versus_layout = property(_get_versus_layout)

    def render_comment(self):
        comment = post_markup_filter(self.comment)
        return render_filter(comment, self.syntax or 'textile')

    def clean_rosters(self):
        for r in self.rosters.distinct():
            self.rosters.remove(r)
        self.save()

    class Meta:
        ordering = ['-id', ]

from apps.tabletop.signals import setup_signals
setup_signals()
