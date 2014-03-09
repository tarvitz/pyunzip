from datetime import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic
from apps.files.models import Attachment
from django.core.urlresolvers import reverse
from utils.models import copy_fields
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from apps.djangosphinx.models import SphinxSearch
from apps.core.helpers import post_markup_filter, render_filter

NEWS_STATUSES = (
    ('approved', _("approved")),
    ('rejected', _("rejeceted")),
    ('queued', _("queued")),
    ('revision', _('revision')),
)


# Create your models here.
class Category(models.Model):
    name = models.CharField(_('Category'), max_length=100, blank=False, null=False)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class AbstractSubstance(models.Model):
    title = models.CharField(
        _('title'), max_length=255, null=False)
    author = models.CharField(_('author'), max_length=40)
    content = models.CharField(_('content'), max_length=10240)
    author_ip = models.IPAddressField(_('ip address', blank=True))
    syntax = models.CharField(
        _('syntax'), max_length=20,
        blank=True,
        choices=settings.SYNTAX
    )

    class Meta:
        abstract = True


# noinspection PyUnresolvedReferences,PyUnresolvedReferences
class AbstractNews(models.Model):
    title = models.CharField(
        _('title'), max_length=255,
        null=False
    )
    author = models.CharField(
        _('author'), max_length=255,
        null=False
    )
    editor = models.CharField(
        _('editor'), max_length=255, blank=True
    )
    url = models.CharField(
        _('original URL'), max_length=200, blank=True
    )
    content = models.TextField(
        _('content'), null=False)
    cache_content = models.TextField(
        _('cache content'), blank=True, null=True
    )
    date = models.DateTimeField(
        _('dateTime'), null=False, default=datetime.now)
    approved = models.BooleanField(
        _('approved'), blank=True, default=False)
    author_ip = models.CharField(
        _('author ip address'), max_length=16, blank=True)
    category = models.ForeignKey(Category)
    is_event = models.BooleanField(_('is event'), default=False)
    syntax = models.CharField(
        _('Syntax'), max_length=20, blank=True, null=True,
        choices=settings.SYNTAX
    )
    attachment = models.ForeignKey(Attachment, blank=True, null=True)
    reason = models.CharField(_('reason'), max_length=1024, blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name='owner',
        related_name='%(class)s', default=1
    )
    status = models.CharField(
        choices=NEWS_STATUSES,
        default='queued',
        max_length=32,
    )
    resend = models.BooleanField(
        _('resend'),
        help_text=_("marks if news notification should resend"),
        default=False
    )
    seen_objects = generic.GenericRelation(
        'tracker.SeenObject', object_id_field='object_pk'
    )

    get_title = lambda self: self.title
    get_content = lambda self: self.content

    def __unicode__(self):
        return "News"

    def _get_description(self):
        return self.head_content

    description = property(_get_description)

    def get_head(self):
        if '(cut)' in self.content:
            return self.content[:self.content.index('(cut)')]
        return self.content

    def get_comments(self):
        ct = ContentType.objects.get(app_label='news', model='news')
        return Comment.objects.filter(
            content_type=ct, object_pk=str(self.pk)
        )

    def get_comments_count(self):
        return self.get_comments().count()

    def get_seen_users(self):
        return [i.user for i in self.seen_objects.all()]

    @property
    def head_content(self):
        return self.get_head()

    def get_status_label(self):
        if self.status == 'rejected':
            return 'important'
        elif self.status == 'queued':
            return 'info'
        elif self.status == 'approved':
            return 'success'
        elif self.status == 'revision':
            return 'warning'
        return 'inverse'

    def render(self, field):
        out = post_markup_filter(getattr(self, field))
        return render_filter(out, self.syntax)

    render_content = lambda self: self.render('content')
    render_head_content = lambda self: self.render('head_content')

    class Meta:
        abstract = True


class ArchivedNews(AbstractNews):
    search = SphinxSearch(
        weights={
            'title': 100,
            'head_content': 100,
            'content': 100,
        }
    )

    class Meta:
        verbose_name = _('Archived Article')
        verbose_name_plural = _('Archived News')
        ordering = ['-id']

    #def get_absolute_url(self):
    #    return reverse('apps.news.views.show_archived_article', kwargs={'number': self.id})

    #def unarchive(self):
    #    n = News()
    #    copy_fields(self,n)
    #    n.save()
    #    self.delete()

    def get_absolute_url(self):
        return reverse('news:article-archived', kwargs={'id': self.id})

    class Meta:
        permissions = (
            ('edit_archived_news', _('Can edit archived news')),
        )
        verbose_name = _('Archived news')
        verbose_name_plural = _('Archived news')


class News(AbstractNews):
    search = SphinxSearch(
        weights={
            'title': 100,
            'head_content': 100,
            'content': 100,
        }
    )
    comments = generic.GenericRelation(
        Comment,
        content_type_field='content_type',
        object_id_field='object_pk'
    )

    #def get_absolute_url(self):
    #    return reverse('news:article', kwargs={'number': self.id})

    def archive(self):
        a = ArchivedNews()
        copy_fields(self, a)
        #actions with comments
        a.save()
        old_ct = ContentType.objects.get(app_label='news', model='news')
        new_ct = ContentType.objects.get(app_label='news', model='archivednews')
        comments = Comment.objects.filter(
            content_type=old_ct, object_pk=str(self.id)
        )
        for c in comments:
            c.content_type = new_ct
            c.object_pk = str(a.id)
            c.save()
        self.delete()

        return a

    def get_content_plain(self):
        if self.head_content:
            return "%s\n%s\n%s" % (
                self.title, self.head_content, self.content
            )
        else:
            return "%s\%s" % (self.title, self.content)

    def get_absolute_url(self):
        return reverse('news:article', kwargs={'pk': self.pk, })

    def get_edit_url(self):
        return reverse('news:news-update', args=(self.pk, ))

    def get_approve_url(self):
        return reverse('news:article-action', args=(self.pk, 'approve'))

    def get_disapprove_url(self):
        return reverse('news:article-action', args=(self.pk, 'unapprove'))

    def get_delete_url(self):
        return reverse('news:article-action', args=(self.pk, 'delete'))

    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('News')
        permissions = (
            ('edit_news', _('Can edit news')),
            ('del_restore_comments', _('Can delete and restore comments')),
            ('edit_comments', _('Can edit comments')),
            ('purge_comments', _('Can purge comments')),
        )


class MeatingType(models.Model):
    title = models.CharField(_("title"), max_length=64)
    codename = models.CharField(_("codename"), unique=True, max_length=32)
    __unicode__ = lambda s: "%s [%s]" % (s.title, s.codename)

    class Meta:
        verbose_name = _("Meating Type")
        verbose_name_plural = _("Meating Types")


# noinspection PyShadowingBuiltins
class Meating(models.Model):
    title = models.CharField(_("title"), max_length=256)
    type = models.ForeignKey(MeatingType, verbose_name=_("type"), default=1)
    owner = models.ForeignKey(
        User, verbose_name=_("owner"),
        related_name='meating_owner_set')
    members = models.ManyToManyField(
        User, verbose_name=_("members"),
        related_name='meating_user_sets'
    )
    content = models.TextField(_("content"), max_length=4096)
    syntax = models.CharField(
        _('syntax'), max_length=20, blank=True,
        null=True, choices=settings.SYNTAX,
        default='textile'
    )
    created_on = models.DateTimeField(
        _("created on"), auto_now_add=True
    )
    updated_on = models.DateTimeField(
        _("updated on"), auto_now=True
    )
    is_approved = models.BooleanField(_('approved'), default=False)
    author_ipv4 = models.CharField(
        _('author ip address'),
        max_length=16, blank=True
    )
    author_ipv6 = models.CharField(
        _('author ip address'),
        max_length=16, blank=True
    )

    def get_absolute_url(self):
        return reverse('news:meating', args=(self.id, ))

    def __unicode__(self):
        return "%s [%s]" % (self.title, self.type.title)

    class Meta:
        verbose_name = _("Meating")
        verbose_name_plural = _("Meatings")
        ordering = ['created_on', '-id', ]

from signals import setup_signals
setup_signals()
