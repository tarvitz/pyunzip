import os

from django.contrib.contenttypes import generic
from django.conf import settings
from django.db import models
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from apps.files.helpers import ZipPack
from apps.files import actions

from django.core.urlresolvers import reverse


from django.core.exceptions import ValidationError
from django.http import Http404

#Abstract Classes

class IncomeFile(models.Model):
    file = models.FileField(_('File'),upload_to=lambda s, fn: "files/%s/%s" % (str(s.owner.id), fn))
    description = models.CharField(_('Description'),max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    upload_date = models.DateTimeField(_('Upload date'))
    class Meta:
        abstract = True #do not store this model into db

class IncomeReplay(models.Model):
    file = models.FileField(_('Replay'),upload_to=os.path.join(settings.MEDIA_ROOT,'replays/'))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
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
        ordering = ['-release_number', '-patch']
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
    choices= [(1,'1vs1'),(2,'2vs2'),(3,'3vs3'),(4,'4vs4'),(5,'set'),(0,'non standard')]
    winners = list()
    for i in xrange(8): winners.append((i+1, _('Team')+ " %i" % (i+1)))
    name = models.CharField(_('Name'), max_length=100, null=False)
    version = models.ForeignKey(Version) #Version by itself includes game name and its version ;) for example DoW SS
    upload_date = models.DateTimeField(_('Upload date'), null=False)
    type = models.IntegerField(_('Type'), max_length=30,choices=choices,null=False)
    nonstd_layout = models.CharField(_('Non Std layout'), max_length=30, blank=True)
    teams  = models.CharField(_('Teams'), max_length=200, blank=True)
    races = models.CharField(_('Races'), max_length=100, null=False)
    winner = models.IntegerField(_('Winner'), choices=winners, max_length=30, null=False)
    #author = models.CharField(_('Author'), max_length=100, null=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    replay = models.FileField(_('File'),upload_to=lambda s, fn: "replays/%s/%s" % (str(s.author.id), fn))
    #implement it =\
    #replay = BinCaseFileField(_('File'),upload_to=os.path.join(settings.MEDIA_ROOT,"replays/"))
    #users_announcement = models.ForeignKey(Announcement,null=True,blank=True)
    comments = models.TextField(_('Comments'),blank=True)
    is_set = models.BooleanField(_('is set'), blank=True, default=False)
    syntax = models.CharField(_('Syntax'),max_length=20,choices=settings.SYNTAX,blank=True,null=True) 

    actions = []
    get_title = lambda self: self.name
    get_content = lambda self: self.comments
    owner = lambda self: self.author
    def get_absolute_url(self):
        #return "/replays/%i" % self.id
        return reverse('files:replay', kwargs={'number': self.id})

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
        if self.type == 5:
            return 'set'
        elif self.type == 0:
            return 'unstd'
        else:
            return str(self.type)+'vs'+str(self.type)
    
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
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('files:galleries', args=(self.pk, ))

    class Meta:
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')


class Image(models.Model): 
    #def upload_to(self, filename):
    #    return 'images/galleries/%s/%s' % (str(self.owner.id), filename)

    def valid_alias(value):
        if value.replace('_','').isalnum():
            return value
        raise ValidationError("You should use only letters, digits and _")
    title = models.CharField(_('Title'), max_length=100)
    alias = models.CharField(
        _('Alias'), max_length=32, blank=True,
        unique=True,
        null=True,
        help_text=_('Fast name to access unit'),
        validators=[valid_alias]) #shorter, wiser
    comments = models.TextField(_('Comments'))
    gallery = models.ForeignKey(Gallery, verbose_name=_("gallery"))
    image = models.ImageField(
        _('Image'), upload_to=lambda s, fn: "images/galleries/%s/%s" % (str(s.owner.id), fn)
    )
    thumbnail = models.ImageField(
        _('Thumbnail'),
        upload_to=os.path.join(settings.MEDIA_ROOT,"images/galleries/thumbnails/")
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    comment_objects = generic.GenericRelation(
        'comments.Comment',
        object_id_field='object_pk'
    )

    actions = []

    class Meta:
        permissions = (
            ('can_upload', 'Can upload images'),
            ('delete_images', 'Can delete images'),
        )
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        ordering = ['-id', ]
        
    get_title = lambda self: self.title

    def generate_thumbnail(self,size=(200,200)):
        if not self.image:
            return
        from PIL import Image
        from cStringIO import StringIO
        image = Image.open(StringIO(self.image.file.read()))
        path = os.path.join('images/galleries/thumbnails',str(self.owner.id))
        upload_path = os.path.join(settings.MEDIA_ROOT, path)
        try:
            os.stat(upload_path)
        except OSError as (errno, err):
            if errno == 2:
                try:
                    os.makedirs(
                        os.path.join(settings.MEDIA_ROOT, path)
                    )
                except:
                    raise Http404("Could not make dir, please contact with administrator")
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
        return reverse('files:image', args=(self.pk, ))

    def get_edit_url(self):
        return reverse('files:image-edit', args=(self.pk, ))

    def get_delete_url(self):
        return reverse('files:image-delete', args=(self.pk, ))

    def __unicode__(self):
        return "Images"


class File(IncomeFile):
    url = models.URLField(_('Original URL'),blank=True)
    actions = [actions.file_delete_qset, ]
    def show_user(self):
        return self.owner.username
    show_user.short_description = _('owner')    

    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')


class UserFile(models.Model):
    title = models.CharField(_('title'), max_length=256, blank=True, null=True)
    file = models.FileField(
        _('file'), upload_to=lambda s, fn: "user/%s/files/%s" % (str(s.owner.id), fn)
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_file_set')
    plain_type = models.CharField(
        _("plain type"), help_text=_("plain type for "),
        max_length=256, default='octet/stream',
        blank=True, null=True
    )
    actions = []
    size = models.PositiveIntegerField(_('size'), help_text=_('file size'), default=0)

    def get_file_link(self):
        link = os.path.join(settings.MEDIA_URL, self.file.name)
        name = link[:40] + " ..." if len(link) > 40 else link
        return "<a href='%s'>%s</a>" % (
            link,
            name
        )

    def get_file_name(self):
        if '/' in self.file.name:
            name = self.file.name[self.file.name.rindex('/') + 1:]
            name = name[:40] + " ..." if len(name) > 40 else name
            return name
        return self.file.name

    def get_delete_url(self):
        return reverse('files:file-delete', args=(self.pk,))

    def get_file_size(self):
        try:
            return self.file.size
        except OSError:
            return 0

    def delete(self, *args, **kwargs):
        try:
            os.unlink(self.file.path)
        except OSError:
            pass
        super(UserFile, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.title or "User %s file" % (self.owner.id, )

    class Meta:
        verbose_name = _("User file")
        verbose_name_plural = _("User files")

from apps.files.signals import setup_signals
setup_signals()
