# coding: utf-8

from apps.helpers.diggpaginator import DiggPaginator as Paginator
from apps.news.models import News, Meating, ArchivedNews, Event, EventWatch
from apps.news.forms import (
    ArticleModelForm, AddMeatingForm, ArticleStatusForm, EventForm,
    EventParticipateForm
)
from apps.comments.forms import CommentForm

from apps.core import get_skin_template

from apps.core.shortcuts import direct_to_template
from apps.core.helpers import get_content_type

from django.core.paginator import InvalidPage, EmptyPage
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect

from django.contrib.comments.models import Comment

from django.core.urlresolvers import reverse, reverse_lazy
from datetime import datetime,timedelta

from apps.core.helpers import (
    paginate, can_act, get_int_or_zero
)
from apps.core.decorators import (
    has_permission,
)
from apps.core.helpers import render_to, get_object_or_None

from django.views import generic
from apps.core.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator


class NewsListView(generic.ListView):
    template_name = 'news.html'
    paginate_by = settings.OBJECTS_ON_PAGE
    paginator_class = Paginator
    model = News

    def get_queryset(self):
        queryset = super(NewsListView, self).get_queryset()
        order = ('-date', )

        if not self.request.user.has_perm('news.edit_news'):
            return queryset.filter(approved=True).order_by(*order)
        return queryset.order_by(*order)

    def get_context_data(self, **kwargs):
        context = super(NewsListView, self).get_context_data(**kwargs)
        context.update({
            'news': {
                'object_list': context['object_list']
            }
        })
        return context

def search_article(request):
    template = get_skin_template(request.user, "news/search.html")
    return render_to_response(template, {'form':''},
    context_instance=RequestContext(request))


class NewsDetail(generic.DetailView):
    template_name = 'news/article.html'
    model = News

    def get_context_data(self, **kwargs):
        context = super(NewsDetail, self).get_context_data(**kwargs)
        page = get_int_or_zero(self.request.GET.get('page', 0))
        form = CommentForm(None, request=self.request, initial={
            'app_n_model': 'news.news', 'obj_id': self.kwargs.get('number', 0),
            'url': self.request.META.get('PATH_INFO', ''),
            'page': page
        })
        paginator = Paginator(self.object.comments.all(),
                              settings.OBJECTS_ON_PAGE)
        try:
            comments = paginator.page(page)
        except (EmptyPage, InvalidPage):
            comments = paginator.page(1)

        context.update({
            'form': form,
            'article': context['object'],
            'comments': comments,
            'paginator': paginator
        })
        return context

    def dispatch(self, request, *args, **kwargs):
        return super(NewsDetail, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(NewsDetail, self).get_queryset()
        if not self.request.user.has_perm('news.edit_news'):
            return queryset.filter(approved=True)
        return queryset


class NewsUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = 'news/action_article.html'
    model = News
    form_class = ArticleModelForm

    def get_form_kwargs(self):
        kwargs = super(NewsUpdateView, self).get_form_kwargs()
        kwargs.update({
            'request': self.request
        })
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        if not request.user.has_perm('news.edit_news'):
            raise PermissionDenied("permission denied")
        return super(NewsUpdateView, self).dispatch(request, *args, **kwargs)


#@obsolete
@login_required
@can_act
@render_to('news/add.html')
def add_article(request, id=None, edit_flag=False):
    can_edit =  request.user.has_perm('news.edit_news') #if smb can edit news
    instance = get_object_or_404(News, pk=id) if edit_flag else None

    form = ArticleModelForm(
        request.POST, request.FILES, request=request, instance=instance
    )
    if request.method == 'POST':
        if form.is_valid():
            article = form.save(commit=False)
            user = request.user
            has_useractivity = hasattr(user, 'useractivity')
            last_action_time = getattr(user.useractivity, 'last_action_time') if has_useractivity else None
            if last_action_time is not None and not user.is_superuser:
                if last_action_time > datetime.now() - timedelta(minutes=2):
                    return {'redirect': '/article/add/timeout'}
            article.owner = request.user
            article.save()
            user.useractivity.last_action_time = datetime.now()
            user.useractivity.save()
            redirect_path = article.get_absolute_url() if article.is_approved else reverse('news:article-created')

            return {'redirect': redirect_path}

    return {'form': form, 'edit_flag': edit_flag}

@login_required
@render_to('news/news_user.html')
def news_user(request):
    news = request.user.news.all().order_by('-date', '-id')
    return {'news': news}


def view_meatings(request):
    template = 'meatings.html'
    meatings = Meating.objects.all()
    meatings = paginate(meatings, request.GET.get('page', 1), pages=20)
    return direct_to_template(request, template, {'meatings': meatings})

def view_meating(request, id):
    template = 'meating.html'
    meating = get_object_or_None(Meating, id=id)
    return direct_to_template(request, template, {'meating': meating})

@has_permission('news.add_meating')
def add_meating(request):
    template = 'add_meating.html'
    form = AddMeatingForm(request.POST or None, request=request)
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()
            form.save_m2m()
            return HttpResponseRedirect(reverse('news:index'))
    return direct_to_template(request, template, {'form': form})


class EventPermissionMixin(object):
    @method_decorator(has_permission('news.change_event'))
    def dispatch(self, request, *args, **kwargs):
        return super(EventPermissionMixin, self).dispatch(request, *args,
                                                          **kwargs)


# CBV
class EventCreateView(EventPermissionMixin, generic.CreateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'


class EventListView(EventPermissionMixin, generic.ListView):
    model = Event
    paginator_class = Paginator
    paginate_by = settings.OBJECTS_ON_PAGE
    template_name = 'events/events.html'


class EventView(generic.DetailView):
    model = Event
    template_name = 'events/event.html'

    def get_context_data(self, **kwargs):
        context = super(EventView, self).get_context_data(**kwargs)
        # create watch instance to mark this event is watched by user
        if (not self.object.is_finished
                and self.request.user.is_authenticated()):
            watch, created = EventWatch.objects.get_or_create(
                event=self.object,
                user=self.request.user)
        event_ct = get_content_type(Event)
        comments = Comment.objects.filter(content_type=event_ct,
                                          object_pk=self.get_object().pk)
        comments = paginate(
            comments, get_int_or_zero(self.request.GET.get('page', 1) or 1),
            pages=settings.OBJECTS_ON_PAGE
        )
        context.update({
            'comments': comments
        })
        return context


class EventUpdateView(EventPermissionMixin, generic.UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'


class EventDeleteView(EventPermissionMixin, generic.DeleteView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('news:events')


class EventParticipateView(generic.UpdateView):
    model = Event
    form_class = EventParticipateForm
    template_name = 'events/event_form.html'

    def get_context_data(self, **kwargs):
        context = super(EventParticipateView, self).get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        form.instance.participants.add(self.request.user)
        form.instance.save()
        return redirect(self.get_success_url())