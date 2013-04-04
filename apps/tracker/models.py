# coding: utf-8
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

# Create your models here.

class SeenObject(models.Model):
    #std allocation
    content_type = models.ForeignKey(ContentType,
        verbose_name=_('content type'),
        related_name='content_type_set_for_%(class)s')
    object_pk = models.TextField(_('Object ID'))
    content_object = generic.GenericForeignKey(ct_field='content_type',fk_field='object_pk')
    user = models.ForeignKey(User)
