from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _, pgettext_lazy
from django.core.urlresolvers import reverse

from apps.files.models import Attachment
from apps.utils.models import copy_fields

from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.contenttypes import generic

from apps.core.helpers import post_markup_filter, render_filter

NEWS_STATUSES = (
    ('approved', _("approved")),
    ('rejected', _("rejeceted")),
    ('queued', _("queued")),
    ('revision', _('revision')),
)


# Create your models here.
class Category(models.Model):
    name = models.CharField(_('Category'), max_length=100, blank=False,
                            null=False)

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
    reason = models.CharField(_('reason'), max_length=1024, blank=True,
                              null=True)
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

    def get_title(self):
        return self.title

    def get_content(self):
        return self.content

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
    class Meta:
        verbose_name = _('Archived Article')
        verbose_name_plural = _('Archived News')
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse('news:article-archived', kwargs={'id': self.id})

    class Meta:
        permissions = (
            ('edit_archived_news', _('Can edit archived news')),
        )
        verbose_name = _('Archived news')
        verbose_name_plural = _('Archived news')


class News(AbstractNews):
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
        new_ct = ContentType.objects.get(app_label='news',
                                         model='archivednews')
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


EVENT_TYPE_CHOICES = (
    ('game', _("Game")),
    ('tournament', _("Tournament")),
    ('order', pgettext_lazy("cart order", "Order")),
    ('pre-release', pgettext_lazy('pre-release of smth', 'Pre-release')),
    ('release', pgettext_lazy('release of smth', 'Release'))
)

EVENT_LEAGUE_CHOICES = (
    ('wh40k', _("Warhammer 40000")),
    #('whfb', _("Warhammer fantasy battle"))
    ('mtg', _("Magic the gathering")),
    ('board', _("Board gaming"))
)


class EventPlace(models.Model):
    title = models.CharField(_("title"), max_length=512,
                             help_text=_("event place title"))
    address = models.CharField(_("address"), max_length=1024,
                               help_text=_("event place address"),
                               blank=True, null=True)
    contacts = models.CharField(_("contacts"), max_length=256,
                                help_text=_("contacts/help who to find it"),
                                blank=True, null=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("Event Place")
        verbose_name_plural = _("Event Places")


class Event(models.Model):
    """ different events model container for all-people notification usage
    """
    title = models.CharField(_("title"), help_text=_("event title"),
                             max_length=256)
    content = models.CharField(
        _("content"),
        help_text=_(
            "content event text, description, further manual and so on"),
        max_length=settings.MAX_DOCUMENT_SIZE
    )
    content_html = models.TextField(
        _("content html"),
        help_text=_("rendered html content"), blank=True, null=True
    )
    date_start = models.DateTimeField(
        _("date start"), help_text=_("when event date starts")
    )
    date_end = models.DateTimeField(
        _("date end"), help_text=_("when event date ends"),
        blank=True, null=True
    )
    type = models.CharField(
        _("type"), max_length=16,
        choices=EVENT_TYPE_CHOICES, default='game'
    )
    league = models.CharField(
        _("league"), max_length=32,
        help_text=_("game league"),
        choices=EVENT_LEAGUE_CHOICES, default='wh40k',
        blank=True, null=True
    )
    place = models.ForeignKey(
        'news.EventPlace', related_name='event_place_set',
        blank=True, null=True, verbose_name=_("event place")
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='event_users_sets',
        help_text=_("participants would take a part in the event"),
        blank=True, null=True
    )
    is_finished = models.BooleanField(
        _('is finished'), default=False
    )
    is_all_day = models.BooleanField(
        _('is all day'), default=False,
        help_text=_("marks if event could place whole day"),
    )

    comments = generic.GenericRelation(
        'comments.Comment',
        object_id_field='object_pk'
    )

    def __unicode__(self):
        return u'%s [%s]' % (self.title, self.type)

    # urls
    def get_absolute_url(self):
        return reverse('news:event', args=(self.pk, ))

    def get_edit_url(self):
        return reverse('news:event-update', args=(self.pk, ))

    def get_delete_url(self):
        return reverse('news:event-delete', args=(self.pk, ))

    def get_join_url(self):
        return reverse('news:event-join', args=(self.pk, ))

    # properties
    def get_type(self):
        idx = [self.type in i[0] for i in EVENT_TYPE_CHOICES].index(True)
        return EVENT_TYPE_CHOICES[idx][1]

    def render_content(self, field='content'):
        """
        renders content into html for better performance and security issues
        """
        out = post_markup_filter(getattr(self, field))
        return render_filter(out, settings.DEFAULT_SYNTAX)

    class Meta:
        ordering = ['-is_finished', 'date_start', ]
        verbose_name = _("Event")
        verbose_name_plural = _("Events")


class EventWatch(models.Model):
    event = models.ForeignKey('news.Event', related_name='event_watch_set',
                              verbose_name=_("event"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='event_watch_user_set',
                             verbose_name=_("user"))
    created_on = models.DateTimeField(_('created on'), auto_now=True,
                                      default=datetime.now)

    def __unicode__(self):
        return self.event.title + " " + self.user.get_username()

    class Meta:
        verbose_name = _("Event watch")
        verbose_name_plural = _("Event watches")
        unique_together = (('event', 'user'), )


from signals import setup_signals
setup_signals()
