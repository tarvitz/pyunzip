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

class Codex(models.Model):
    content_type = models.ForeignKey(ContentType,
        verbose_name=_('content type'),
        related_name="ct_set_for_%(class)s")
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey(ct_field="content type",
        fk_field="object_id")
    title = models.CharField(_('Title'), max_length=128)
    revisions = models.CommaSeparatedIntegerField(_('Revisions'), max_length=64)
    
    def bound(self):
        try:
            return self.content_type.model_class().objects.get(pk=self.object_id)
        except:
            return None
    
    def __unicode__(self):
        return self.bound().__unicode__()

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
    codex = models.ForeignKey(Codex, blank=True, null=True)
    custom_codex = models.CharField(_('Custom Codex'),max_length=50,blank=True,null=True)
    revision = models.IntegerField(_('Revision'), validators=[valid_revision,])
    pts = models.IntegerField(_('pts')) #we should make A LOT OF CHECK UPS :( within
    syntax = models.CharField(_('Syntax'), max_length=20,blank=True,null=True,choices=settings.SYNTAX)

    is_orphan = models.NullBooleanField(_('Orphan'),default=False,blank=True,null=True) 
    search = SphinxSearch(weights={'title': 30, 'comments': 30})

    def show_player(self):
       if hasattr(self.user,'nickname'): return self.user.nickname
       if self.player: return self.player
       if self.owner: return self.owner.nickname
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

