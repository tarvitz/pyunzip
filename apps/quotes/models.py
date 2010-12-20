# coding: utf-8
import apps.tagging.fields

from datetime import datetime

from django.db                  import models
from django.utils.translation   import ugettext_lazy as _
from django.contrib.auth.models import User

from utils.models import copy_fields
from utils.middleware import threadlocals

from utils import text
from django.core.urlresolvers import reverse

class Quote(models.Model):

    moderator   = models.ForeignKey(User, related_name='quotes_approved',
                    verbose_name=_('quote moderator'))
    author      = models.ForeignKey(User, related_name='quotes_posted',
                    verbose_name=_('quote author'), blank=True, null=True)

    date_add    = models.DateTimeField(_('date add'))
    date_pub    = models.DateTimeField(_('date approved'), auto_now_add=True)
    
    text        = models.CharField(_('contents'), max_length=4096)

    rate        = models.IntegerField(_('rate'), default=0)

    sender_ip   = models.IPAddressField(_('sender ip'), blank=True, null=True)

    tags        = apps.tagging.fields.TagField()

    def __unicode__(self):
	    return (_('quote #%s') % self.id).capitalize()

    get_preview = lambda self: text.preview(self.text, 15) #first 15 words

    get_moderator = lambda self: self.moderator.nickname or self.moderator.username
    
    #get_author = lambda self: self.author.nickname or self.author.username
    
    def _get_moderator(self):
        if self.moderator.is_superuser:
            return "<span style='color: #E37BC0;'>%s</span>" % (self.moderator.nickname or self.moderator.username)
        if self.moderator.is_staff:
            return "<span style='color: gold;'>%s</span>" % (self.moderator.nickname or self.moderator.username)
        return self.moderator.nickname or self.moderator.username
    
    get_moderator = property(_get_moderator)
    
    def _get_author(self):
        return self.author.nickname or self.author.username
    get_author = property(_get_author)
    
    def get_absolute_url(self):
        return reverse('apps.quotes.views.quote', kwargs={'id':self.id})
        #return "/quotes/quote/%i" % self.id #FIXME :( 

    class Meta:
        verbose_name = _('approved quote')
        verbose_name_plural = _('approved quotes')
        ordering = ('-date_pub',)

class QueueQuote(models.Model):
    
    author      = models.ForeignKey(User, related_name='quotes_proposed',
                        verbose_name=_('quote author'), blank=True, null=True)
    date_add    = models.DateTimeField(_('date add'), auto_now_add=True)
    text        = models.CharField(_('contents'), max_length=4096)
    sender_ip   = models.IPAddressField(_('sender ip'), blank=True, null=True)
    seen_by     = models.ManyToManyField(User, related_name='seen_quotes', blank=True, null=True)
    rejected_by = models.ManyToManyField(User, related_name='rejected_quotes', blank=True, null=True)

    tags        = apps.tagging.fields.TagField()

    def __unicode__(self):
	    return (_('unapproved quote #%s') % self.id).capitalize()

    def save(self, *args, **kwargs):
        if not self.pk:
            user = threadlocals.get_current_user()
            if user and user.is_authenticated():
                self.author = user
        super(QueueQuote, self).save(*args, **kwargs)

    def approve(self, user):
        q = Quote()
        copy_fields(self, q)
        q.date_pub = datetime.now()
        q.moderator = user
        q.save()
        self.delete()
        return q

    get_preview = lambda self: text.preview(self.text, 15) #first 15 words

    get_author = lambda self: self.author.nickname or self.author.username

    class Meta:
        verbose_name = _('unapproved quote')
        verbose_name_plural = _('unapproved quotes')
        ordering = ('-date_add',)
