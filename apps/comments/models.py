# coding: utf-8
from .managers import CommentManager

from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible

from datetime import datetime
# Create your models here.

COMMENT_MAX_LENGTH = getattr(settings, 'COMMENT_MAX_LENGTH', 3000)


class BaseCommentAbstractModel(models.Model):
    """
    An abstract base class that any custom comment models probably should
    subclass.
    """

    # Content-object field
    content_type = models.ForeignKey(
        ContentType, verbose_name=_('content type'),
        related_name="content_type_set_for_%(class)s"
    )
    object_pk = models.TextField(_('object ID'))
    content_object = generic.GenericForeignKey(ct_field="content_type",
                                               fk_field="object_pk")

    # Metadata about the comment
    site = models.ForeignKey(Site)

    class Meta:
        abstract = True

    def get_content_object_url(self):
        """
        Get a URL suitable for redirecting to the content object.
        """
        return urlresolvers.reverse(
            "comments-url-redirect",
            args=(self.content_type_id, self.object_pk)
        )


@python_2_unicode_compatible
class Comment(BaseCommentAbstractModel):
    """
    A user comment about some object.
    """

    # Who posted this comment? If ``user`` is set then it was an authenticated
    # user; otherwise at least user_name should have been set and the comment
    # was posted by a non-authenticated user.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'),
                    blank=True, null=True, related_name="%(class)s_comments")
    user_name = models.CharField(_("user's name"), max_length=50, blank=True)
    user_email = models.EmailField(_("user's email address"), blank=True)
    user_url = models.URLField(_("user's URL"), blank=True)

    comment = models.TextField(_('comment'), max_length=COMMENT_MAX_LENGTH)

    # Metadata about the comment
    submit_date = models.DateTimeField(_('date/time submitted'), default=None)
    ip_address = models.GenericIPAddressField(
        _('IP address'), unpack_ipv4=True, blank=True, null=True)
    is_public = models.BooleanField(
        _('is public'), default=True,
        help_text=_('Uncheck this box to make the comment effectively '
                    'disappear from the site.'))
    is_removed = models.BooleanField(
        _('is removed'), default=False,
        help_text=_('Check this box if the comment is inappropriate. '
                    'A "This comment has been removed" message will be '
                    'displayed instead.')
    )
    syntax = models.CharField(
        _('Syntax'), max_length=50, null=True, blank=True,
        choices=settings.SYNTAX)

    cache_comment = models.TextField(
        _("cache comment"), null=True, blank=True
    )

    # Manager
    objects = CommentManager()

    class Meta:
        db_table = "django_comments"
        ordering = ('submit_date',)
        permissions = [("can_moderate", "Can moderate comments")]
        verbose_name = _('comment')
        verbose_name_plural = _('comments')

    def __str__(self):
        return "%s: %s..." % (self.name, self.comment[:50])

    def save(self, *args, **kwargs):
        if self.submit_date is None:
            self.submit_date = timezone.now()
        super(Comment, self).save(*args, **kwargs)

    def _get_userinfo(self):
        """
        Get a dictionary that pulls together information about the poster
        safely for both authenticated and non-authenticated comments.

        This dict will have ``name``, ``email``, and ``url`` fields.
        """
        if not hasattr(self, "_userinfo"):
            userinfo = {
                "name": self.user_name,
                "email": self.user_email,
                "url": self.user_url
            }
            if self.user_id:
                u = self.user
                if u.email:
                    userinfo["email"] = u.email

                # If the user has a full name, use that for the user name.
                # However, a given user_name overrides the raw user.username,
                # so only use that if this comment has no associated name.
                if u.get_full_name():
                    userinfo["name"] = self.user.get_full_name()
                elif not self.user_name:
                    userinfo["name"] = u.get_username()
            self._userinfo = userinfo
        return self._userinfo
    userinfo = property(_get_userinfo, doc=_get_userinfo.__doc__)

    def _get_name(self):
        return self.userinfo["name"]

    def _set_name(self, val):
        if self.user_id:
            raise AttributeError(
                _("This comment was posted by an authenticated user and "
                  "thus the name is read-only.")
            )
        self.user_name = val

    name = property(
        _get_name, _set_name,
        doc="The name of the user who posted this comment"
    )

    def _get_email(self):
        return self.userinfo["email"]

    def _set_email(self, val):
        if self.user_id:
            raise AttributeError(
                _("This comment was posted by an authenticated user and"
                  " thus the email is read-only."))
        self.user_email = val
    email = property(_get_email, _set_email,
                     doc="The email of the user who posted this comment")

    def _get_url(self):
        return self.userinfo["url"]

    def _set_url(self, val):
        self.user_url = val
    url = property(_get_url, _set_url,
                   doc="The URL given by the user who posted this comment")

    def get_absolute_url(self, anchor_pattern="#c%(id)s"):
        return self.get_content_object_url() + (anchor_pattern % self.__dict__)

    def get_as_text(self):
        """
        Return this comment as plain text.  Useful for emails.
        """
        d = {
            'user': self.user or self.name,
            'date': self.submit_date,
            'comment': self.comment,
            'domain': self.site.domain,
            'url': self.get_absolute_url()
        }
        return _(
            'Posted by %(user)s at %(date)s\n\n%(comment)s\n\n'
            'http://%(domain)s%(url)s'
        ) % d

    def get_edit_url(self):
        return reverse('comments:comment-update', args=(self.pk, ))

    def get_delete_url(self):
        return reverse('core:comment-delete', args=(self.pk, ))

    def render_comment(self):
        """ renturns comment in render"""
        from apps.core.helpers import post_markup_filter, render_filter
        return render_filter(post_markup_filter(self.comment),
                             self.syntax or 'textile')

    def get_content(self):
        return self.comment

    def get_title(self):
        if len(self.comment) > 100:
            return "%s ..." % self.comment[0:100]
        else:
            return self.comment


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
    @staticmethod
    def get_absolute_url():
        return '/'

    def get_subscription_remove_url(self):
        return reverse('comments:subscription-remove', args=(self.pk, ))

    def get_api_subscription_read(self):
        return reverse('api:commentwatch-detail', args=(self.pk, ))

    def get_new_comments(self):
        """ get new comments

        if CommentWatch instance is_disabled, returns blank Comment queryset
        identifies that subscription has no new comments at all

        :return: Comment queryset
        :rtype: QuerySet
        """
        if self.is_disabled:
            return Comment.objects.none()
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


from .signals import setup_signals
setup_signals()