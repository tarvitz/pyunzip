# coding: utf-8
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from apps.vote.managers import BestManager

# Create your models here.

class AbstractVote(models.Model):
    content_type = models.ForeignKey(ContentType,
        verbose_name=_('content type'),
        related_name="content_type_set_for_%(class)s")
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content type", fk_field="object_pk")

    class Meta:
        abstract = True

class Rate(AbstractVote):
    rate = models.IntegerField(_('Rate'))
    user = models.ForeignKey(User)
    comment = models.TextField(_('Comment'),max_length=512,blank=True,null=True) # we could give little comment for it
    def __unicode__(self):
        return str(self.rate)

class Vote(AbstractVote):
    votes = models.IntegerField(_('Votes'),blank=True)
    score = models.FloatField(_('Vote score'), blank=True)
    #is there reasonable to use ManyToMany intentions ?
    #user = models.ForeignKey(User, verbose_name=_('user')) 
    users = models.ManyToManyField(User)
    rates = models.ManyToManyField(Rate)
    #managers 
    objects = models.Manager() 
    best_objects = BestManager()
    #class Meta:
    
    def __unicode__(self):
        return str(self.rating)
        #if self.score is not None and self.votes is not None:
        #    return u"%f" % (self.score/self.votes)
    def _get_total(self):
        return u"%0.2f" % (self.votes*5)
    total = property(_get_total)
    
    def _get_total_rating(self):
        total_rating = 5
        return total_rating
    total_rating = property(_get_total_rating)

    def _get_rating(self):
        rating = "%0.2f" % float(self.score/self.votes)
        return rating
    rating = property(_get_rating)
    def get_subclass_name(self):
        return self.content_type.model #model_class().__doc__.split('(')[0].lower()
    subclass_name = property(get_subclass_name)
    def get_object(self):
        try:
            return self.content_type.model_class().objects.get(pk=self.object_pk)
        except:
            return None
    object = property(get_object)
