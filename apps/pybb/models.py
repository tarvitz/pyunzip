from datetime import datetime

from django.db import models
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from apps.pybb import settings as pybb_settings
from apps.core.helpers import post_markup_filter, render_filter
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.validators import MinValueValidator, MaxValueValidator

MARKUP_CHOICES = (
    ('textile', 'textile'),
    ('bbcode', 'bbcode'),
    ('markdown', 'markdown'),
)


class Category(models.Model):
    name = models.CharField(_('Name'), max_length=80)
    position = models.IntegerField(_('Position'), blank=True, default=0)

    class Meta:
        ordering = ['position']
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __unicode__(self):
        return self.name

    def forum_count(self):
        return self.forums.all().count()

    def get_absolute_url(self):
        return reverse('pybb:category', args=[self.id])

    @property
    def topics(self):
        return Topic.objects.filter(forum__category=self).select_related()

    @property
    def posts(self):
        return Post.objects.filter(
            topic__forum__category=self).select_related()


class Forum(models.Model):
    category = models.ForeignKey(Category, related_name='forums',
                                 verbose_name=_('Category'))
    name = models.CharField(_('Name'), max_length=80)
    position = models.IntegerField(_('Position'), blank=True, default=0)
    description = models.TextField(_('Description'), blank=True, default='')
    moderators = models.ManyToManyField(User, blank=True, null=True,
                                        verbose_name=_('Moderators'))
    updated = models.DateTimeField(_('Updated'), null=True)
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)
    css_icon = models.CharField(_("Css icon"), blank=True, default='',
                                max_length=64)
    is_hidden = models.BooleanField(_('is hidden'), default=False)
    is_private = models.BooleanField(_('is private'), default=False)
    participants = models.ManyToManyField(
        'auth.User', related_name='forum_user_sets',
        help_text=_("private participants list"),
        blank=True, null=True)

    class Meta:
        ordering = ['position']
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')

    def __unicode__(self):
        return self.name

    def topic_count(self):
        return self.topics.all().count()

    def get_absolute_url(self):
        return reverse('pybb:forum', args=[self.id])

    @property
    def posts(self):
        return Post.objects.filter(topic__forum=self).select_related()

    @property
    def last_post(self):
        posts = self.posts.order_by('-created').select_related()
        try:
            return posts[0]
        except IndexError:
            return None


class Topic(models.Model):
    forum = models.ForeignKey(Forum, related_name='topics',
                              verbose_name=_('Forum'))
    name = models.CharField(_('Subject'), max_length=255)
    created = models.DateTimeField(_('Created'), null=True)
    updated = models.DateTimeField(_('Updated'), null=True)
    user = models.ForeignKey(User, verbose_name=_('User'))
    views = models.IntegerField(_('Views count'), blank=True, default=0)
    sticky = models.BooleanField(_('Sticky'), blank=True, default=False)
    closed = models.BooleanField(_('Closed'), blank=True, default=False)
    subscribers = models.ManyToManyField(
        User, related_name='subscriptions', verbose_name=_('Subscribers'),
        blank=True
    )
    post_count = models.IntegerField(_('Post count'), blank=True, default=0)

    class Meta:
        ordering = ['-created']
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')

    def __unicode__(self):
        return self.name

    @property
    def owner(self):
        return self.user

    @property
    def head(self):
        return self.posts.all().order_by('created').select_related()[0]

    @property
    def last_post(self):
        return self.posts.all().order_by('-created').select_related()[0]

    def get_last_page(self):
        return (self.posts.count() / settings.OBJECTS_ON_PAGE) + 1

    @property
    def poll(self):
        instance = None
        try:
            instance = self.poll_topic_set.get()
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            pass
        return instance

    def save(self, *args, **kwargs):
        if self.id is None:
            self.created = datetime.now()
        super(Topic, self).save(*args, **kwargs)

    def update_read(self, user):
        read, new = Read.objects.get_or_create(user=user, topic=self)
        if not new:
            read.time = datetime.now()
            read.save()

    def get_poll_add_url(self):
        return reverse_lazy('pybb:poll-add', args=(self.pk, ))

    def get_absolute_url(self):
        return reverse_lazy('pybb:posts', args=(self.pk, ))


class AnonymousPost(models.Model):
    session_key = models.CharField(_('Session key'), max_length=40)
    topic = models.ForeignKey(Topic, verbose_name=_('Topic'), blank=True)
    created = models.DateTimeField(_('Created'), auto_now_add=True)

    markup = models.CharField(_('Markup'), max_length=15, blank=True,
                              default='')
    body = models.TextField(_('Message'), blank=True, default='')

    class Meta:
        verbose_name = _('Anonymous post')
        verbose_name_plural = _('Anonymous posts')


class Post(models.Model):
    topic = models.ForeignKey(Topic, related_name='posts',
                              verbose_name=_('Topic'))
    user = models.ForeignKey(User, related_name='posts',
                             verbose_name=_('User'))
    created = models.DateTimeField(_('Created'), blank=True,
                                   auto_now=True, default=datetime.now)
    updated = models.DateTimeField(_('Updated'), blank=True, null=True,
                                   auto_now_add=True, default=datetime.now)
    markup = models.CharField(
        _('Markup'), max_length=15, default=pybb_settings.DEFAULT_MARKUP,
        choices=MARKUP_CHOICES)
    body = models.TextField(_('Message'))
    body_html = models.TextField(_('HTML version'))
    body_text = models.TextField(_('Text version'))
    user_ip = models.IPAddressField(_('User IP'), blank=True, default='')

    class Meta:
        ordering = ['created']
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def summary(self):
        limit = 50
        tail = len(self.body) > limit and '...' or ''
        return self.body[:limit] + tail

    __unicode__ = summary

    def save(self, *args, **kwargs):
        if self.created is None:
            self.created = datetime.now()
        self.body_html = self.render("body")

        new = self.id is None

        if new:
            self.topic.updated = datetime.now()
            self.topic.post_count += 1
            self.topic.save()
            self.topic.forum.updated = self.topic.updated
            self.topic.forum.post_count += 1
            self.topic.forum.save()

        super(Post, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('pybb:posts', args=[self.topic.pk]) + (
            '?page=%(page)s#post-%(post)s' % {
                'page': self.topic.get_last_page(),
                'post': self.pk
            }
        )

    def render(self, field):
        out = post_markup_filter(getattr(self, field))
        return render_filter(out, self.markup)

    render_body = lambda self: self.render("body")

    def delete(self, *args, **kwargs):
        self_id = self.id
        head_post_id = self.topic.posts.order_by('created')[0].id
        super(Post, self).delete(*args, **kwargs)

        self.topic.post_count -= 1
        self.topic.save()
        self.topic.forum.post_count -= 1
        self.topic.forum.save()

        if self_id == head_post_id:
            self.topic.delete()

    def get_body_messges_count(self):
        return len(self.body.split(' '))


class Read(models.Model):
    """
    For each topic that user has entered the time
    is logged to this model.
    """

    user = models.ForeignKey(User, verbose_name=_('User'))
    topic = models.ForeignKey(Topic, verbose_name=_('Topic'))
    time = models.DateTimeField(_('Time'), blank=True)

    class Meta:
        unique_together = ['user', 'topic']
        verbose_name = _('Read')
        verbose_name_plural = _('Reads')

    def save(self, *args, **kwargs):
        if self.time is None:
            self.time = datetime.now()
        super(Read, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'T[%d], U[%d]: %s' % (self.topic.id, self.user.id,
                                      unicode(self.time))


class Poll(models.Model):
    topic = models.ForeignKey(Topic, related_name='poll_topic_set',
                              unique=True)
    title = models.CharField(_('title'), max_length=2048,
                             help_text=_("poll title"))
    voted_amount = models.PositiveIntegerField(
        _("voted amount"), help_text=_("amount of voted user, cache field"),
        default=0
    )
    items_amount = models.PositiveIntegerField(
        _('items amount'),
        help_text=_('positive amount of poll items for further creation'),
        default=2
    )
    is_multiple = models.BooleanField(
        _("is multiple"), help_text=_("is multiple select allowed"),
        default=False
    )
    is_prepared = models.BooleanField(
        _('is prepared'),
        help_text=_('marks if poll is prepared to rock n roll'),
        default=False
    )
    is_finished = models.BooleanField(
        _('is finished'), help_text=_("marks if poll is finished"),
        default=False
    )
    date_expire = models.DateTimeField(
        _("date expire"), help_text=_("date then poll is expired"),
        blank=True, null=True
    )

    @property
    def items(self):
        return self.poll_item_poll_set

    @property
    def answers(self):
        return self.answer_poll_set

    def get_voted_amount(self, commit=True):
        amount = sum(self.items.values('voted_amount') or [0])
        if amount != self.voted_amount:
            self.voted_amount = amount
            if commit:
                self.save()
        return amount

    def get_configure_url(self):
        return reverse_lazy('pybb:poll-configure', args=(self.pk, ))

    def get_update_url(self):
        return reverse_lazy('pybb:poll-update', args=(self.pk, ))

    def get_delete_url(self):
        return reverse_lazy('pybb:poll-delete', args=(self.pk, ))

    def get_vote_url(self):
        return reverse_lazy('pybb:poll-vote', args=(self.pk, ))

    def get_voted_users(self):
        qset = PollAnswer.objects.filter(poll=self)
        if 'psycopg' in settings.DATABASES['default']['ENGINE']:
            return User.objects.filter(
                pk__in=qset.distinct('user').values('user'))
        users = set()
        for poll_answer in qset:
            users.add(poll_answer.user.pk)
        return User.objects.filter(pk__in=list(users))

    def reload_score(self, commit=True):
        self.voted_amount = len(self.get_voted_users())
        for item in self.items.all():
            item.reload_score()
        if commit:
            self.save()
        return self

    def __unicode__(self):
        return '%s [%i]' % (self.title, self.voted_amount)

    class Meta:
        verbose_name = _("Poll")
        verbose_name_plural = _("Polls")


class PollItem(models.Model):
    poll = models.ForeignKey(Poll, related_name='poll_item_poll_set')
    title = models.CharField(_('title'), max_length=2048)
    voted_amount = models.PositiveIntegerField(
        _("voted amount"), help_text=_("amount of voted user, cache field"),
        default=0
    )
    score = models.DecimalField(
        _('score'), help_text=_('score in percent'), default=0,
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)])

    @property
    def answers(self):
        return self.answer_poll_item_set

    def reload_score(self, commit=True):
        """saves ``PollItem instance`` with reloaded percent score

        :param commit: saves instance when ``True``, ``True`` by default
        :return: self ``instance``
        """
        amount = self.poll.answers.count()
        voted = self.answers.count()
        self.score = voted / (amount * 0.01)
        if commit:
            self.save()
        return self

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _("Poll item")
        verbose_name_plural = _("Poll items")


class PollAnswer(models.Model):
    poll = models.ForeignKey(Poll, related_name='answer_poll_set')
    poll_item = models.ForeignKey(PollItem,
                                  related_name='answer_poll_item_set')
    user = models.ForeignKey('auth.User', related_name='answer_user_set')

    def __unicode__(self):
        return u'%s: %s' % (self.user.get_username(), self.poll_item.title)

    class Meta:
        verbose_name = _("Poll answer")
        verbose_name_plural = _("Poll answers")


from apps.pybb import signals
signals.setup_signals()
