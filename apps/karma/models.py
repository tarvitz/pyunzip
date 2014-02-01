# coding: utf-8
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
# processin' this we got an error =\
from apps.wh.models import Side
from django.conf import settings
from django.core.urlresolvers import reverse

# debugs an error listed above
#side = __import__('apps.wh.models',0,0,1)

# Create your models here.
class Karma(models.Model):
    comment = models.CharField(_('Comment'), max_length=512, blank=True)
    value = models.IntegerField(_('Power'))
    date = models.DateTimeField(_('Date'), auto_now=True)
    user = models.ForeignKey(User,related_name='karma_owner_set')
    voter = models.ForeignKey(User,related_name='karma_voter_set')
    url = models.URLField(_('URL'),blank=True,null=True)

    def get_karma(self):
        karmas = self._base_manager.filter(user=self.user)
        karma = 0
        for k in karmas:
            karma += k.value
        return karma
    karma = property(get_karma)

    def get_karma_value(self):
        if self.value>0:
            return '+%i' % self.value
        else:
            return '%i' % self.value
    karma_value = property(get_karma_value)

    def show_user(self):
        return self.user.nickname
    show_user.short_description = _('User')

    #def get_status(self):
    def get_absolute_url(self):
        return reverse('url_karma_user',args=(self.user.nickname,))

    class Meta:
        ordering = ['-date']

class KarmaStatus(models.Model):
    codename = models.CharField(_('Codename'),max_length=100,unique=True)
    status = models.CharField(_('Status'),max_length=100)
    value = models.IntegerField(_('Value'))
    is_humor = models.NullBooleanField(_('Humor'),null=True,blank=True)
    description = models.CharField(_('Description'),max_length=1024)
    side = models.ManyToManyField(Side,blank=True)
    is_general = models.BooleanField(_('is General'),blank=True, default=False)
    syntax = models.CharField(_('Syntax'),max_length=20,blank=True,null=True,choices=settings.SYNTAX)    
    def __unicode__(self):
        return "%s" % (self.status)
    def get_absolute_url(self):
        url = reverse('url_karma_status',args=(self.codename,))
        print url
        return url
    class Meta:
        verbose_name = _('Karma Status')
        verbose_name_plural=_('Karma Statuses')
