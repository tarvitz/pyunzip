import math
import datetime

from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect
from django.http import (
    HttpResponseRedirect, HttpResponse, HttpResponseNotFound, Http404)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.urlresolvers import reverse, reverse_lazy

from apps.core.helpers import render_to, get_int_or_zero, get_object_or_None
from apps.pybb.util import render_to, paged, build_form, quote_text
from apps.pybb.models import (
    Category, Forum, Topic, AnonymousPost, Post,
    Profile,
    PrivateMessage,
    Poll, PollItem, PollAnswer
)
from apps.pybb.forms import (
    AddPostForm, EditProfileForm, EditPostForm, UserSearchForm, CreatePMForm,
    AddPollForm, PollItemForm, PollItemBaseinlineFormset, UpdatePollForm,
    SingleVotePollForm, MultipleVotePollForm, AgreeForm
)
from apps.pybb import settings as pybb_settings
from apps.pybb.anonymous_post import (
    handle_anonymous_post, load_anonymous_post, delete_anonymous_post)
from django.views.decorators.csrf import csrf_exempt
from django.views import generic
from django.utils.decorators import method_decorator
from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView
from django.core.exceptions import PermissionDenied


def index_ctx(request):
    quick = {'posts': Post.objects.count(),
             'topics': Topic.objects.count(),
             'users': User.objects.count(),
             'last_topics': Topic.objects.all().select_related()[:pybb_settings.QUICK_TOPICS_NUMBER],
             'last_posts': Post.objects.order_by('-created').select_related()[:pybb_settings.QUICK_POSTS_NUMBER],
             }

    cats = {}
    forums = {}

    for forum in Forum.objects.filter(is_hidden=False).select_related():
        cat = cats.setdefault(forum.category.id,
            {'cat': forum.category, 'forums': []})
        cat['forums'].append(forum)
        forums[forum.id] = forum

    cmpdef = lambda a, b: cmp(a['cat'].position, b['cat'].position)
    cats = sorted(cats.values(), cmpdef)

    return {'cats': cats,
            'quick': quick,
            }
index = render_to('pybb/index.html')(index_ctx)


def show_category_ctx(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    quick = {'posts': category.posts.count(),
             'topics': category.topics.count(),
             'last_topics': category.topics.select_related()[:pybb_settings.QUICK_TOPICS_NUMBER],
             'last_posts': category.posts.order_by('-created').select_related()[:pybb_settings.QUICK_POSTS_NUMBER],
             }
    return {'category': category,
            'quick': quick,
            }
show_category = render_to('pybb/category.html')(show_category_ctx)


@paged('topics', pybb_settings.FORUM_PAGE_SIZE)
def show_forum_ctx(request, forum_id):
    forum = get_object_or_404(Forum, pk=forum_id)
    topics = forum.topics.order_by('-sticky', '-updated').select_related()
    quick = {'posts': forum.post_count,
             'topics': forum.topics.count(),
             'last_topics': forum.topics.all().select_related()[:pybb_settings.QUICK_TOPICS_NUMBER],
             'last_posts': forum.posts.order_by('-created').select_related()[:pybb_settings.QUICK_POSTS_NUMBER],
             }

    return {'forum': forum,
            'topics': topics,
            'quick': quick,
            'paged_qs': topics,
            }
show_forum = render_to('pybb/forum.html')(show_forum_ctx)


@paged('posts', pybb_settings.TOPIC_PAGE_SIZE)
def show_topic_ctx(request, topic_id):
    try:
        topic = Topic.objects.select_related().get(pk=topic_id)
    except Topic.DoesNotExist:
        raise Http404()
    topic.views += 1
    topic.save()


    if request.user.is_authenticated():
        topic.update_read(request.user)

    posts = topic.posts.all().select_related()

    if pybb_settings.FREEZE_FIRST_POST:
        first_post = topic.posts.order_by('created')[0]
    else:
        first_post = None
    last_post = topic.posts.order_by('-created')[0]

    profiles = Profile.objects.filter(user__pk__in=set(x.user.id for x in posts))
    profiles = dict((x.user_id, x) for x in profiles)

    for post in posts:
        post.user.pybb_profile = profiles[post.user.id]

    initial = {}
    apost = load_anonymous_post(request, topic)
    if apost:
        initial = {'markup': apost.markup, 'body': apost.body}

    if request.user.is_authenticated():
        initial = {'markup': request.user.pybb_profile.markup}

    form = AddPostForm(topic=topic, initial=initial)

    moderator = request.user.is_superuser or\
        request.user in topic.forum.moderators.all()
    if request.user.is_authenticated() and request.user in topic.subscribers.all():
        subscribed = True
    else:
        subscribed = False

    poll_form_class = SingleVotePollForm
    if topic.poll and topic.poll.is_multiple:
        poll_form_class = MultipleVotePollForm
    poll_form = poll_form_class(None, poll=topic.poll) if topic.poll else None
    return {'topic': topic,
            'last_post': last_post,
            'first_post': first_post,
            'form': form,
            'moderator': moderator,
            'subscribed': subscribed,
            'paged_qs': posts,
            'poll_form': poll_form
            }
show_topic = render_to('pybb/topic.html')(show_topic_ctx)


@login_required
def add_post_ctx(request, forum_id, topic_id):
    forum = None
    topic = None

    if forum_id:
        forum = get_object_or_404(Forum, pk=forum_id)
    elif topic_id:
        topic = get_object_or_404(Topic, pk=topic_id)

    if topic and topic.closed:
        return HttpResponseRedirect(topic.get_absolute_url())

    if not request.user.is_authenticated():
        return handle_anonymous_post(request, topic_id)

    # GET request
    if 'GET' == request.method:
        try:
            quote_id = int(request.GET.get('quote_id'))
        except TypeError:
            quote = ''
        else:
            qpost = get_object_or_404(Post, pk=quote_id)
            quote = quote_text(
                qpost.body_text,
                request.user.pybb_profile.markup
            )

        apost = load_anonymous_post(request, topic)
        if apost:
            markup = apost.markup
            body = apost.body
        else:
            markup = request.user.pybb_profile.markup
            body = quote

        form = build_form(AddPostForm, request, topic=topic, forum=forum,
                          user=request.user, initial={'markup': markup, 'body': body})

    # POST request
    else:
        delete_anonymous_post(request, topic)

        ip = request.META.get('REMOTE_ADDR', '')
        form = build_form(AddPostForm, request, topic=topic, forum=forum,
                          user=request.user, ip=ip)

        if form.is_valid():
            post = form.save();
            return HttpResponseRedirect(post.get_absolute_url())


    return {'form': form,
            'topic': topic,
            'forum': forum,
            }

add_post = render_to('pybb/add_post.html')(add_post_ctx)


def user_ctx(request, username):
    user = get_object_or_404(User, nickname=username)
    topic_count = Topic.objects.filter(user=user).count()
    return {'profile': user,
            'topic_count': topic_count,
            }
user = render_to('pybb/user.html')(user_ctx)


def show_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    count = post.topic.posts.filter(created__lt=post.created).count() + 1
    page = math.ceil(count / float(pybb_settings.TOPIC_PAGE_SIZE))
    url = '%s?page=%d#post-%d' % (reverse('pybb_topic', args=[post.topic.id]), page, post.id)
    return HttpResponseRedirect(url)


@login_required
def edit_profile_ctx(request):
    form = build_form(EditProfileForm, request, instance=request.user.pybb_profile)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('pybb_edit_profile'))
    return {'form': form,
            'profile': request.user.pybb_profile,
            }
edit_profile = render_to('pybb/edit_profile.html')(edit_profile_ctx)


@login_required
def edit_post_ctx(request, post_id):
    from apps.pybb.templatetags.pybb_extras import pybb_editable_by

    post = get_object_or_404(Post, pk=post_id)
    if not pybb_editable_by(post, request.user):
        return HttpResponseRedirect(post.get_absolute_url())

    form = build_form(EditPostForm, request, instance=post)

    if form.is_valid():
        post = form.save()
        return HttpResponseRedirect(post.get_absolute_url())

    return {'form': form,
            'post': post,
            }
edit_post = render_to('pybb/edit_post.html')(edit_post_ctx)


@login_required
def stick_topic(request, topic_id):
    from apps.pybb.templatetags.pybb_extras import pybb_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if pybb_moderated_by(topic, request.user):
        if not topic.sticky:
            topic.sticky = True
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def unstick_topic(request, topic_id):
    from apps.pybb.templatetags.pybb_extras import pybb_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if pybb_moderated_by(topic, request.user):
        if topic.sticky:
            topic.sticky = False
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@csrf_exempt
@login_required
def delete_post_ctx(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    last_post = post.topic.posts.order_by('-created')[0]
    topic = post.topic

    allowed = False
    if request.user.is_superuser or\
        request.user in post.topic.forum.moderators.all() or \
        (post.user == request.user and post == last_post):
        allowed = True

    if not allowed:
        return HttpResponseRedirect(post.get_absolute_url())

    if 'POST' == request.method:
        topic = post.topic
        forum = post.topic.forum
        post.delete()

        try:
            Topic.objects.get(pk=topic.id)
        except Topic.DoesNotExist:
            return HttpResponseRedirect(forum.get_absolute_url())
        else:
            return HttpResponseRedirect(topic.get_absolute_url())
    else:
        return {'post': post,
                }
delete_post = render_to('pybb/delete_post.html')(delete_post_ctx)


@login_required
def close_topic(request, topic_id):
    from apps.pybb.templatetags.pybb_extras import pybb_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if pybb_moderated_by(topic, request.user):
        if not topic.closed:
            topic.closed = True
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@login_required
def open_topic(request, topic_id):
    from apps.pybb.templatetags.pybb_extras import pybb_moderated_by

    topic = get_object_or_404(Topic, pk=topic_id)
    if pybb_moderated_by(topic, request.user):
        if topic.closed:
            topic.closed = False
            topic.save()
    return HttpResponseRedirect(topic.get_absolute_url())


@render_to('pybb/users.html')
@paged('users', pybb_settings.USERS_PAGE_SIZE)
def users_ctx(request):
    users = User.objects.order_by('username').filter(is_active=True)
    form = UserSearchForm(request.GET)
    users = form.filter(users)
    return {'paged_qs': users,
            'form': form,
            }
users = paged('users', pybb_settings.USERS_PAGE_SIZE)(users_ctx)


@login_required
def delete_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.remove(request.user)
    if 'from_topic' in request.GET:
        return HttpResponseRedirect(reverse('pybb_topic', args=[topic.id]))
    else:
        return HttpResponseRedirect(reverse('pybb_edit_profile'))


@login_required
def add_subscription(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    topic.subscribers.add(request.user)
    return HttpResponseRedirect(reverse('pybb_topic', args=[topic.id]))


@login_required
def create_pm_ctx(request):
    recipient = request.GET.get('recipient', '')
    form = build_form(CreatePMForm, request, user=request.user,
                      initial={'markup': request.user.pybb_profile.markup,
                               'recipient': recipient})

    if form.is_valid():
        post = form.save();
        return HttpResponseRedirect(reverse('pybb_pm_outbox'))

    return {'form': form,
            'pm_mode': 'create',
            }
create_pm = render_to('pybb/pm/create_pm.html')(create_pm_ctx)


@login_required
def pm_outbox_ctx(request):
    messages = PrivateMessage.objects.filter(src_user=request.user)
    return {'messages': messages,
            'pm_mode': 'outbox',
            }
pm_outbox = render_to('pybb/pm/outbox.html')(pm_outbox_ctx)


@login_required
def pm_inbox_ctx(request):
    messages = PrivateMessage.objects.filter(dst_user=request.user)
    return {'messages': messages,
            'pm_mode': 'inbox',
            }
pm_inbox = render_to('pybb/pm/inbox.html')(pm_inbox_ctx)


@login_required
def show_pm_ctx(request, pm_id):
    msg = get_object_or_404(PrivateMessage, pk=pm_id)
    if not request.user in [msg.dst_user, msg.src_user]:
        raise PermissionDenied('not allowed')
    if request.user == msg.dst_user:
        pm_mode = 'inbox'
        if not msg.read:
            msg.read = True
            msg.save()
        post_user = msg.src_user
    else:
        pm_mode = 'outbox'
        post_user = msg.dst_user
    return {'msg': msg,
            'pm_mode': pm_mode,
            'post_user': post_user,
            }
show_pm = render_to('pybb/pm/message.html')(show_pm_ctx)


@login_required
def switch_theme(request, theme):
    themes = [i[0] for i in settings.FORUM_THEMES]
    if theme in themes:
        if not request.user.settings:
            request.user.settings = {}
        request.user.settings['forum_theme'] = settings.FORUM_THEMES[themes.index(theme)][1]
        request.user.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


class PollMixin(object):
    def get_poll_object(self):
        if not hasattr(self, 'poll'):
            self.poll = get_object_or_404(Poll, pk=self.kwargs.get('pk', 0))
        return self.poll


class ManagePollView(generic.FormView):
    """ Manage poll view to existent topic """
    form_class = AddPollForm
    template_name = 'pybb/poll_add.html'

    def get_form_class(self):
        if self.kwargs.get('update', False):
            return UpdatePollForm
        elif self.kwargs.get('delete', False):
            return AgreeForm
        return super(ManagePollView, self).get_form_class()

    def get_form_kwargs(self):
        if self.kwargs.get('update', False):
            instance = get_object_or_404(Poll, pk=self.kwargs.get('pk', 0))
        elif self.kwargs.get('delete', False):
            pass
        else:
            topic = get_object_or_404(Topic, pk=self.kwargs.get('pk', 0))
            instance = topic.poll
        kwargs = super(ManagePollView, self).get_form_kwargs()
        if not self.kwargs.get('delete', False):
            kwargs.update({
                'instance': instance
            })
        return kwargs

    def get_success_url(self, pk):
        return reverse_lazy('pybb_poll_configure', args=(pk, ))

    def form_valid(self, form):
        if self.kwargs.get('delete', False):
            instance = get_object_or_404(Poll, pk=self.kwargs.get('pk', 0))
            redirect_url = instance.topic.get_absolute_url()
            instance.delete()
        else:
            if not self.kwargs.get('update', False):
                form.instance.topic = get_object_or_404(
                    Topic, pk=self.kwargs.get('pk', 0)
                )
            instance = form.save()
            redirect_url = self.get_success_url(pk=instance.pk)
        return redirect(redirect_url)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if self.kwargs.get('delete', False):
            if not request.user.has_perm('pybb.change_poll'):
                raise PermissionDenied("not allowed")
        return super(ManagePollView, self).dispatch(request, *args, **kwargs)


class ConfigurePollView(PollMixin, generic.FormView):
    template_name = 'pybb/poll_configure.html'

    def get_form_kwargs(self):
        self.get_poll_object()
        kwargs = super(ConfigurePollView, self).get_form_kwargs()
        kwargs.update({
            'instance': self.poll
        })
        return kwargs

    def get_form_class(self):
        self.get_poll_object()
        amount = (
            self.poll.items_amount if not self.poll.items.count()
            else self.poll.items_amount - self.poll.items.count()
        )
        formset = inlineformset_factory(
            Poll, PollItem, formset=PollItemBaseinlineFormset,
            form=PollItemForm,
            fk_name='poll', fields=('title', ),
            can_delete=self.poll.poll_item_poll_set.count(),
            extra=amount,
            max_num=settings.MAXIMUM_POLL_ITEMS_AMOUNT)
        return formset

    def get_success_url(self):
        self.get_poll_object()
        return self.poll.topic.get_absolute_url()

    def form_valid(self, form):
        form.save()
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(ConfigurePollView, self).get_context_data(**kwargs)
        context.update({
            'poll': self.get_poll_object()
        })
        return context


class PollVoteView(PollMixin, generic.CreateView):
    """ PollVoteView operates with user vote single or multiple vote poll. """
    model = PollAnswer
    # get_form_class alters SingleVotePollForm to multple one
    form_class = SingleVotePollForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(PollVoteView, self).dispatch(request, *args, **kwargs)

    def get_form_class(self):
        if self.get_poll_object().is_multiple:
            return MultipleVotePollForm
        return super(PollVoteView, self).get_form_class()

    def get_form_kwargs(self):
        kwargs = super(PollVoteView, self).get_form_kwargs()
        kwargs.update({'poll': self.get_poll_object()})
        return kwargs

    def form_valid(self, form):
        """ save PollAnswer

        :param form: PollForm
        :return: success redirect url
        """
        votes = form.cleaned_data['vote']
        if hasattr(votes, '__iter__'):
            for poll_item in votes:
                poll_answer, created = PollAnswer.objects.get_or_create(
                    poll_item=poll_item, user=self.request.user,
                    poll=poll_item.poll
                )
        else:
            poll_answer, created = PollAnswer.objects.get_or_create(
                poll_item=votes, user=self.request.user,
                poll=votes.poll
            )
        if created:
            poll_answer.poll_item.poll.reload_score()

        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.get_poll_object().topic.get_absolute_url()

    def get(self, request, *args, **kwargs):
        raise PermissionDenied("not allowed")


def add_poll_wizard(request, pk, step=None):
    extra = int(request.POST.get('0-items_amount', 1))
    PollItemsFormset = formset_factory(PollItemForm, extra=extra)

    wizard = AddPollWizard.as_view(
        [AddPollForm, PollItemsFormset], url_name='pybb_poll_add',
        done_step_name='finished')
    return wizard(request, pk=pk, step=step)


class AddPollWizard(NamedUrlSessionWizardView):
    template_name = 'pybb/poll_wizard.html'

    def done(self, form_list, **kwargs):
        poll_form = form_list[0]
        poll_item_formset = form_list[1]
        return redirect('/')

    def get_step_url(self, step):
        return reverse_lazy(self.url_name,
                            args=(self.kwargs.get('pk', 0), step))

    def get_template_names(self):
        return self.template_name
