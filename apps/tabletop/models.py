from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.files.models import Attachment
from django.core.urlresolvers import reverse
from utils.models import copy_fields
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from apps.wh.models import Side

class Roster(models.Model):
    owner = models.ForeignKey(User,related_name='roster_owner')
    title = models.CharField(_('Title'),max_length=100)
    user = models.ForeignKey(User,blank=True,null=True,related_name='user')
    player = models.CharField(_('Player'),blank=True,max_length=32)
    roster = models.TextField(_('Roster'),max_length=4096)
    #may cause an errors as CharField was moved to TextField without database
    #changes
    comments = models.TextField(_('Comments'),max_length=10240,blank=True,null=True)
    race = models.ForeignKey(Side,related_name='race',blank=True,null=True)
    custom_race = models.CharField(_('Custom Race'),max_length=50,blank=True,null=True)
    pts = models.IntegerField(_('pts')) #we should make A LOT OF CHECK UPS :( within
    syntax = models.CharField(_('Syntax'), max_length=20,blank=True,null=True,choices=settings.SYNTAX)

    is_orphan = models.NullBooleanField(_('Orphan'),default=False,blank=True,null=True) 

    def show_player(self):
       if hasattr(self.user,'nickname'): return self.user.nickname
       if self.player: return self.player
       if self.owner: return self.owner.nickname
    show_player.short_description = _('Player')

    def show_race(self):
        return self.race or self.custom_race
    show_race.short_description = _('Race')

    def get_title(self):
        return self.title

    def __unicode__(self):
        player_name = self.show_player()
        race = self.show_race()
        return "%s [%s:%s:%i]" % (self.title,player_name,race,self.pts)
        #self.user.nickname or self.player

    def save(self,*args,**kwargs):
        from apps.core.helpers import get_user
        user = get_user(nickname=self.player)
        if user:
            self.user = user
        #We can not choose race and custom race once
        if self.race and self.custom_race:
            self.custom_race = None
        super(Roster,self).save(*args,**kwargs)
        #return self
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
    
    def _show_races(self):
        races = list()
        for r in self.users.distinct():
            races.append(r.race)
        return races
    races = property(_show_races)

    def clean_rosters(self):
        for r in self.users.distinct():
            self.users.remove(r)
        self.save()

    class Meta:
        ordering = ['-id',]
        #permissions = (
        #)
        #abstract = True

