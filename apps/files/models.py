import os

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
#from apps.bincase.fields import BinCaseField as BinCaseFileField
from cStringIO import StringIO
from apps.files.helpers import ZipPack
from django.core.urlresolvers import reverse
from apps.core.models import Announcement
from apps.djangosphinx.models import SphinxSearch

#Abstract Classes

class IncomeFile(models.Model):
    file = models.FileField(_('File'),upload_to=os.path.join(settings.MEDIA_ROOT,'files/'))
    description = models.CharField(_('Description'),max_length=255)
    owner = models.ForeignKey(User)
    upload_date = models.DateTimeField(_('Upload date'))
    class Meta:
        abstract = True #do not store this model into db

class IncomeReplay(models.Model):
    file = models.FileField(_('Replay'),upload_to=os.path.join(settings.MEDIA_ROOT,'replays/'))
    owner = models.ForeignKey(User)
    upload_date = models.DateTimeField(_('Uploaded date'))
    class Meta:
        abstract = True

#Real classes
# Create your models here.
class Game(models.Model):
    name = models.CharField(_('Name'), max_length=100, null=False)
    short_name = models.CharField(_('Short name'),max_length=30, null=False)
    def __unicode__(self):
        return self.name

#AKA ADDON!
class Version(models.Model):
    name = models.CharField(_('Addon name'), max_length=100, null=False, blank=True)
    patch = models.CharField(_('Patch version'), max_length=20, null=False)
    release_number = models.IntegerField(_('Release Number'))
    game = models.ForeignKey(Game)
    def __unicode__(self):
        #self.name = self.name.replace('Vanilla','')
        if self.name:
            return "%s: %s v%s" % (self.game.name, self.name, self.patch)
        else:
            return "%s v%s" % (self.game.name, self.patch)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Addon version')
        verbose_name_plural = _('Addon versions')

class Attachment(models.Model):
    attachment = models.FileField(_('Attachment'), upload_to=os.path.join(settings.MEDIA_ROOT,'attachments/'))
    def __unicode__(self):
        return self.attachment.name
"""
class DowReplayNg(IncomeReplay):
    name = models.CharField(_('Name'),max_length=50,null=False)
    #!!!A LOT OF TO ADD!!!
    version_choices = (('dow','Dawn of War'),('wa','Winter Assault'),('dc','Dark Crusade'),('ss','SoulStorm'))
    version = models.CharField(_('Version'),max_length=30,choices=version_choices)
    winner = models.CharField(_('Winner'),max_length=30)
    comments = models.TextField(_('Comments'),blank=True)
    def get_absolute_url(self):
        return "/replays_ng/dow/%s/" % self.id

    #implement adequate saving functional ;(
    #def save(self):
"""        
#TODO: AnonymousReplay :) should it be?
class Replay(models.Model):
    #choices for game type
    choices= [('1','1vs1'),('2','2vs2'),('3','3vs3'),('4','4vs4'),('5','set'),('0','non standard')]
    winners = list()
    for i in xrange(8): winners.append(('%i' % (i+1), _('team')+ " %i" % (i+1)))
    name = models.CharField(_('Name'), max_length=100, null=False)
    version = models.ForeignKey(Version) #Version by itself includes game name and its version ;) for example DoW SS
    upload_date = models.DateTimeField(_('Upload date'), null=False)
    type = models.CharField(_('Type'), max_length=30,choices=choices,null=False)
    nonstd_layout = models.CharField(_('Non Std layout'), max_length=30, blank=True)
    teams  = models.CharField(_('Teams'), max_length=200, blank=True)
    races = models.CharField(_('Races'), max_length=100, null=False)
    winner = models.CharField(_('Winner'), choices=winners, max_length=30, null=False)
    #author = models.CharField(_('Author'), max_length=100, null=False)
    author = models.ForeignKey(User)
    replay = models.FileField(_('File'),upload_to=os.path.join(settings.MEDIA_ROOT,"replays/"))
    #implement it =\
    #replay = BinCaseFileField(_('File'),upload_to=os.path.join(settings.MEDIA_ROOT,"replays/"))
    #users_announcement = models.ForeignKey(Announcement,null=True,blank=True)
    comments = models.TextField(_('Comments'),blank=True)
    is_set = models.BooleanField(_('is set'), blank=True)
    syntax = models.CharField(_('Syntax'),max_length=20,choices=settings.SYNTAX,blank=True,null=True) 
    search = SphinxSearch(weights={
        'title': 30,
        'comment': 40,
    })
    get_title = lambda self: self.name
    get_content = lambda self: self.comments
    owner = lambda self: self.author
    def get_absolute_url(self):
        #return "/replays/%i" % self.id
        return reverse('apps.files.views.show_replay', kwargs={'number': self.id})

    def __unicode__(self):
        return "Replays" 
    def _file(self):
        return self.replay
    file = property(_file)
    
    def show_author(self):
        return self.author.nickname
    show_author.short_description = _('Author')

    @property
    def title(self):
        return self.name
    
    @property
    def type_word(self):
        if self.type == '0': return 'nonstd'
        elif self.type == '1': return 'duel'
        else: return 'team'
    @property
    def get_type(self):
        if self.type == '5':
            return 'set'
        elif self.type == '0' or 0:
            return 'unstd'
        else:
            return self.type+'vs'+self.type
    
    def _get_players_teamlist_new(self):
        if not self.is_set:
            players = self.teams.split(',')
            teams_count = len(self.nonstd_layout.split('vs'))
            teams,team_list = list(),list()
            map = ['0vs0','1vs1','2vs2','3vs3','4vs4']
            if self.type == '0':
                for i in self.nonstd_layout.split('vs'):
                    teams.append(int(i))
            else:
                for i in map[int(self.type)].split('vs'):
                    teams.append(int(i))
            team = ''
            count = 0
            for t in xrange(0,len(teams)):
                for i in xrange(0,teams[t]):
                    if  i != int(teams[t]-1):
                       team += players[i+count] + '/'
                    else:
                        player = players[i+count]
                        team += player#[player.index(' ')+1:]
                team_list.append(team)
                team = ''
                count += int(teams[t])
            return team_list

    def _get_players_teamlist(self):
        if not self.is_set: 
            players = self.teams.split(',')
            teams_count = len(self.nonstd_layout.split('vs'))
            teams, team_list = list(),list()
            map = ['0vs0','1vs1','2vs2','3vs3','4vs4']
            if self.type == "0":
                for i in self.nonstd_layout.split('vs'):
                    teams.append(int(i))
            else:
                for i in map[int(self.type)].split('vs'):
                    teams.append(int(i))
            team = ''
            count = 0
            for t in xrange(0,len(teams)):
                for i in xrange(0,teams[t]): #0->i
                    if t == 0:
                        team += players[i]+' '
                    else:
                        team += players[i+count]+' '
                team_list.append(team)
                team = ''
                count += int(teams[t])
            return team_list
    
    def _get_players_teams(self):
        team_list = self._get_players_teamlist_new()
        teams = ''
        for t in xrange(0,len(team_list)):
            if t != (len(team_list)-1):
                teams +=  team_list[t]+" vs "
                pass
            else:
                teams += team_list[t]
                pass
        return teams
    
    def _get_players_winners(self):
        idx = int(self.winner)
        team_list = self._get_players_teamlist_new()
        return team_list[idx-1]

    player_teams = property(_get_players_teams)
    winner_names = property(_get_players_winners)
    
    #def save(self):
    def _get_replay_type(self):
        type = 'null'
        #import zipfile,bz2
        # toooooo big
        #try:
        #    zinfo = zipfile.ZipFile(StringIO(self.replay.file.read()))
        #    self.replay.file.seek(0)
        #    type = 'zip'
        #    return type
        #except zipfile.BadZipfile:
        #    type = 'plain'
        self.replay.file.seek(0)
        bzinfo = self.replay.file.read(4)
        if bzinfo in ['BZh9']:
            type = 'bz2'
        elif bzinfo in ['PK\x03\x04']:
            type = 'zip'
        return type

    replay_type = property(_get_replay_type)
    
    def _retrieve_zip_info(self):
        #retrieving zip info from file and return them via dict
        if self._get_replay_type() in 'zip':
            #do_actions :)
            rp = ZipPack(buffer=self.replay.file.read())
            self.replay.file.seek(0)
            return rp.get_full_info()
        return {}
    zip_info = property(_retrieve_zip_info)
    def _install_zip_instance(self):
        if self._get_replay_type() in 'zip':
            rp = ZipPack(buffer=self.replay.file.read())
            self.replay.file.seek(0)
            return rp
    replay_pack_instanse = property(_install_zip_instance)

    class Meta:
        ordering = ['-id']
        verbose_name = _('Replay')
        verbose_name_plural = _('Replays')
        permissions = (
            ('can_upload','Can upload replays'),
            ('edit_replay', 'Can edit replay'),
            #('can_delete', 'Can delete replays'), # WAS I DRUNK ?
            ('purge_replays', 'Can purge replays'),
        )
class MetaGallery(models.Model):
    gallery_types = [('tech','technical'),('global', 'global'),('user','user')]
    type = models.CharField(_('Type'), choices=gallery_types,max_length=30,null=False)
    name = models.CharField(_('Name'), max_length=100)
    class Meta:
        abstract = True

class Gallery(MetaGallery):
    #name = models.CharField(_('Name'), max_length=100)
    #owner = models.ForeignKey(User) #common gallery does not include owner
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')

class Image(models.Model):
    title = models.CharField(_('Title'), max_length=100)
    comments = models.TextField(_('Comments'))
    gallery = models.ForeignKey(Gallery)
    image = models.ImageField(_('Image'), upload_to=os.path.join(settings.MEDIA_ROOT, 'images/galleries/'))
    thumbnail = models.ImageField(_('Thumbnail'), upload_to=os.path.join(settings.MEDIA_ROOT,"images/galleries/thumbnails/"))
    owner = models.ForeignKey(User)
    search = SphinxSearch(weights={
        'title': 40,
        'comments': 30,
    })

    class Meta:
        permissions = (
         ('can_upload', 'Can upload images'),
         ('delete_images', 'Can delete images'),
        )
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        
    get_title = lambda self: self.title
     
    def generate_thumbnail(self,size=(200,200)):
        if not self.image:
            return
        from PIL import Image
        from cStringIO import StringIO
        image = Image.open(StringIO(self.image.file.read()))
        path = os.path.join('images/galleries/thumbnails',str(self.owner.id))
        path = os.path.join(path,self.image.file.name.split('/')[-1])
        full_path = os.path.join(settings.MEDIA_ROOT,path)
        x,y = image.size
        sx,sy = size
        if (x > sx or y>sy):
            if x>y: sy = int(y*((sy/(x/100.0))/100.0))
            if y>x: sx = int(x*((sx/(y/100.0))/100.0))
            image = image.resize((sx,sy))
        image.save(full_path)
        self.thumbnail = path
        self.save()
    
    def get_absolute_url(self):
        #return "/image/%i/" % self.id
        return reverse('apps.files.views.show_image', kwargs={'number': self.id})
    
    def __unicode__(self):
        return "Images"

class File(IncomeFile):
    url = models.URLField(_('Original URL'),blank=True)
    
    def show_user(self):
        return self.owner.username
    show_user.short_description = _('owner')    

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')

from apps.files.signals import setup_signals
setup_signals()
