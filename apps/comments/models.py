# coding: utf-8
from django.db import models
from django.db.models import Q
from django.contrib.comments.models import Comment
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse

from apps.core.helpers import post_markup_filter, render_filter

from datetime import datetime
# Create your models here.


Comment.add_to_class(
    'syntax', models.CharField(
        _('Syntax'), max_length=50, null=True, blank=True,
        choices=settings.SYNTAX)
)
Comment.add_to_class(
    'cache_comment', models.TextField(
        _("cache comment"), null=True, blank=True
    )
)

from django.contrib.comments.admin import CommentsAdmin
CommentsAdmin.fieldsets += (
    (
        _('Overload'),
        {
            'fields': ('syntax',)
        }
    )
)


# noinspection PyUnresolvedReferences
class CommentExtension(object):
    def get_edit_url(self):
        return reverse('comments:comment-update', args=(self.pk, ))

    def get_delete_url(self):
        return reverse('core:comment-delete', args=(self.pk, ))

    def render_comment(self):
        """ renturns comment in render"""
        return render_filter(post_markup_filter(self.comment), self.syntax or 'textile')

    def get_content(self):
        return self.comment

    def get_title(self):
        if len(self.comment) > 100:
            return "%s ..." % self.comment[0:100]
        else:
            return self.comment

Comment.__bases__ = Comment.__bases__ + (CommentExtension,)


class CommentWatch(models.Model):
    content_type = models.ForeignKey(
        ContentType, verbose_name=_('content type'),
        related_name='content_type_set_for_%(class)s')
    object_pk = models.PositiveIntegerField(_('object pk'))
    object = generic.GenericForeignKey(ct_field='content_type',
                                       fk_field='object_pk')
    comment = models.ForeignKey('comments.Comment',
                                related_name='comment_watch_set',
                                verbose_name=_("comment"), blank=True,
                                null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='comment_watch_user_set',
                             verbose_name=_("user"))
    created_on = models.DateTimeField(_('created on'), auto_now=True,
                                      default=datetime.now)
    is_disabled = models.BooleanField(
        _("is disabled"), default=False,
        help_text=_("marks if watch is disabled for present moment"))
    is_updated = models.BooleanField(
        _("is updated"), default=False,
        help_text=_("marks if comment watch was updated for new comments")
    )

    def __unicode__(self):
        title = (self.object.title if hasattr(self.object, 'title')
                    else self.object.__unicode__())
        return title + " " + self.user.get_username()

    # urls
    def get_subscription_remove_url(self):
        return reverse('comments:subscription-remove', args=(self.pk, ))

    def get_api_subscription_read(self):
        return reverse('api:commentwatch-detail', args=(self.pk, ))

    def get_new_comments(self):
        qset = Q()
        if self.comment:
            qset = Q(submit_date__gt=self.comment.submit_date)
        comments = Comment.objects.filter(
            content_type=self.content_type,
            object_pk=self.object_pk,
        ).filter(qset)
        return comments

    class Meta:
        verbose_name = _("Comment watch")
        verbose_name_plural = _("Comment watches")
        unique_together = (('content_type', 'object_pk', 'user'), )
