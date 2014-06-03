from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

from apps.files.models import Attachment
from apps.utils.models import copy_fields
import apps.tagging.fields


# Create your models here.
"""
class Category(models.Model):
    name = models.CharField(_('Category'), max_length=100, blank=False, null=False)
    
    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name=_('Category')
        verbose_name_plural=_('Categories')
        abstract = True
"""

class AbstractPost(models.Model):
    title = models.CharField(_('Title'), max_length=255,null=False)
    author = models.CharField(_('Author'), max_length=30,null=False)
    #editor = models.CharField(_('Editor'), max_length=30,blank=True)
    url = models.CharField(_('URL'),max_length=200, blank=True)
    #head_content = models.TextField(_('Head content'), blank=True, null=True)
    content =  models.TextField(_('Content'), null=False)
    date = models.DateTimeField(_('DateTime'),null=False)
    #is that normal to approve selves blog posts ?
    approved = models.BooleanField(_('Approved'),blank=True, default=False)
    author_ip = models.CharField(_('Author IP address'), max_length=16, blank=True)
    #may be it would be better to tag posts?
    #category = models.ForeignKey(Category)
    tags = apps.tagging.fields.TagField()
    #events ? :)
    #is_event = models.BooleanField(_('Is event'))
    attachment = models.ForeignKey(Attachment,blank=True,null=True)
    syntax = models.CharField(_('Syntax'),max_length=20,choices=settings.SYNTAX,blank=True,null=True)  
    #wise alias ;) onto head_content
    get_title = lambda self: self.title
    get_content = lambda self: self.content
    
    def __unicode__(self):
        return "Posts"

    def _get_description(self):
        return self.head_content
    
    description = property(_get_description)
    
    class Meta:
        abstract = True 



class ArchivedPost(AbstractPost):
    class Meta:
        verbose_name = _('Archived Post')
        verbose_name_plural = _('Archived Posts')
        ordering = ['-id']
        #abstarct = True
    #def get_absolute_url(self):
    #    return reverse('apps.news.views.show_archived_article', kwargs={'number': self.id})
    
    #def unarchive(self):
    #    n = News()
    #    copy_fields(self,n)
    #    n.save()
    #    self.delete()
    def get_absolute_url(self):
        pass
        #return reverse('apps.blogs.views.show_archived_post',kwargs={'id':self.id})

class Post(AbstractPost):
    def get_absolute_url(self):
        return reverse('blog:post',kwargs={'id':self.id})

    def archive(self):
        a = ArchivedPost()
        copy_fields(self,a)
        #actions with
        a.save()
        old_ct = ContentType.objects.get(app_label='blogs',model='post')
        new_ct = ContentType.objects.get(app_label='blogs',model='archivedpost')
        comments = Comment.objects.filter(content_type=old_ct,object_pk=str(self.id))
        for c in comments:
            c.content_type = new_ct
            c.object_pk = str(a.id)
            c.save()
        self.delete()

        return a

    def get_absolute_url(self):
            return reverse('blog:post',kwargs={'id':self.id})

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering=['-id']
        """
        permissions = (
            ('edit_news', 'Can edit news'),
            ('del_restore_comments', 'Can delete and restore comments'),
            ('edit_comments', 'Can edit comments'),
            ('purge_comments', 'Can purge comments'),
        )
        """
        #permissions = (
        #)
        #abstarct = True


