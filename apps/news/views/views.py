# Create your views here.
# coding: utf-8
from apps.helpers.diggpaginator import DiggPaginator as Paginator
from apps.news.models import News, Meating, ArchivedNews, Event
from apps.news.forms import (
    ArticleModelForm, AddMeatingForm, ArticleStatusForm, EventForm
)
from apps.core.forms import CommentForm, SphinxSearchForm
from apps.core import get_skin_template
from apps.core.models import Announcement
from apps.core.shortcuts import direct_to_template
from apps.core.forms import ApproveActionForm

from django.core.paginator import InvalidPage, EmptyPage
from django.conf import settings
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.db.models import Q
from django.core.urlresolvers import reverse, reverse_lazy
from datetime import datetime,timedelta

from apps.tracker.decorators import user_visit
from apps.core.helpers import (
    get_settings, paginate, can_act, render_to,
    get_int_or_zero
)
from apps.core.decorators import (
    benchmarking, update_subscription_new, has_permission,
    login_required_json, benchmark as timeit
)
from apps.core.helpers import render_to, get_object_or_None
from apps.core import benchmark
from django.core.cache import cache
from django.views import generic
from apps.core.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator



@benchmarking
def archived_news(request,year='',month='',day=''):
    template = get_skin_template(request.user, 'archived_news.html')
    news = ArchivedNews.objects.all().order_by('-date')
    _pages_ = get_settings(request.user,'news_on_page',10)
    page = request.GET.get('page',1)
    news = paginate(news,page,pages=_pages_)

    return render_to_response(template,{'news':news,'page':news},
        context_instance=RequestContext(request,processors=[benchmark]))
    #return direct_to_template(request,template,{'news':news,'page':news})

#@render_to('news/archived_article.html')
def show_archived_article(request,id):
    ct = ContentType.objects.get(app_label='news',model='archivednews')
    comments = Comment.objects.filter(content_type=ct,object_pk=str(id))
    template = get_skin_template(request.user,'news/archived_article.html')
    try:
        article = ArchivedNews.objects.get(id=id)
    except ArchivedNews.DoesNotExist:
        return HttpResponseRedirect('/article/does/not/exist')
    _pages_ = get_settings(request.user,'news_on_page',30)
    page = request.GET.get('page',1)
    comments = paginate(comments,page,pages=_pages_,jump='#comments')
    #returns via render_to decorator
    return direct_to_template(request,template,{'article':article,'comments':comments})
#test it

#@permission_required('files.purge_replay') #works
#@has_permission('can_test_t') #works
#@cache_page(60*5)
#@benchmarking
@render_to('news.html')
@timeit
def news(request, approved='approved', category=''):
    can_approve_news = None
    if request.user.is_authenticated():
        can_approve_news = request.user.has_perm('news.edit_news')

    page = get_int_or_zero(request.GET.get('page')) or 1
    qset = Q()
    cache_key = 'admin' if can_approve_news else 'everyone'

    if category:
        qset = qset | Q(category__name__icontains=category)
    if not can_approve_news:
        qset = qset | Q(approved=True)
    news = cache.get('news:all:%s' % cache_key)
    if not news:
        news = News.objects.filter(qset).order_by('-date')
        cache.set('news:all:%s' % cache_key, news[:50])
    _pages_ = get_settings(request.user, 'news_on_page', 30)
    news = paginate(
        news, page, pages=_pages_,
        view='apps.news.views.news'
    )
    return {
        'news': news,
        'page': news

    }


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

@render_to('news/article.html')
@user_visit(object_pk='number', ct='news.news')
@update_subscription_new(app_model='news.news', pk_field='number')
def article(request, number=1, object_model='news.news'):
    #template = get_skin_template(request.user,'news/article.html')
    page = request.GET.get('page',1)
    can_edit_news = None
    if hasattr(request.user, 'skin'):
        can_edit_news = request.user.has_perm('news.edit_news')
    #Let staff users allow to get the access for the articles,
    #may be dangerous
    if request.user.is_superuser or can_edit_news:
        article = get_object_or_404(News, id=number)
    else:
        article = (
            get_object_or_None(News, id=number, approved=True) or
            get_object_or_None(News, id=number, owner=request.user)
        )
        if not article:
            raise Http404("Not found")
    news_type = ContentType.objects.get(app_label='news', model='news')
    comments = Comment.objects.filter(content_type=news_type.id, object_pk=str(article.id))
    _pages_ = get_settings(request.user,'comments_on_page',20)
    comments = paginate(comments,page,pages=_pages_)

    form = CommentForm(request=request,initial={'app_n_model':'news.news','obj_id': number,'url':
        request.META.get('PATH_INFO',''),'page':request.GET.get('page','')})
    return {
        'article': article,
        'comments': comments,
        'form': form,
        'page': comments
    }


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

    @method_decorator(user_visit(object_pk='pk', ct='news.news'))
    @method_decorator(update_subscription_new(app_model='news.news',
                                              pk_field='pk'))
    def dispatch(self, request, *args, **kwargs):
        return super(NewsDetail, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super(NewsDetail, self).get_queryset()
        if not self.request.user.has_perm('news.edit_news'):
            return queryset.filter(approved=True)
        return queryset

@login_required
def article_action(request, id=None, action=None):
    if not action or not id:
        return HttpResponseRedirect('/')
    referer = request.META.get('HTTP_REFERER', '/')

    can_approve = request.user.has_perm('news.edit_news')
    redirect_path = ''
    if request.method == 'POST':
        form = ApproveActionForm(request.POST)
        if form.is_valid():
            redirect_path = form.cleaned_data.get('url', None)

    article = get_object_or_404(News, pk=id)

    if not request.user.is_superuser or not can_approve:
        raise Http404(':) go away')
    approved = True if action == 'approve' else False
    article.approved = approved

    if action == 'delete':
        article.delete()
    else:
        article.save()
    return redirect(redirect_path or referer)


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

@login_required
@can_act
@render_to('news/action_article.html')
def action_article(request, id=None, action=None):
    instance = None
    instance = get_object_or_404(News, id=id) if action else None
    approved = getattr(instance, 'approved') if hasattr(instance, 'approved') else False

    if action == 'edit' and instance:
        can_edit = request.user.has_perm('news.can_edit')
        owned = instance.owner == request.user
        if not can_edit:
            if not owned or approved:
                raise Http404("hands off!")

    initial = {
        'content': settings.INITIAL_ARTICLE_CONTENT
    } if not instance else {}
    form = ArticleModelForm(
        request.POST or None,
        request=request,
        instance=instance,
        initial=initial
    )
    if request.method == 'POST':
        if form.is_valid():
            article = form.save(commit=False)
            article.owner = request.user
            article.save()
            # creating announcement
            ct = ContentType.objects.get(
                app_label=article._meta.app_label,
                model=article._meta.module_name
            )
            announcement = Announcement.objects.get_or_create(
                content_type=ct,
                object_pk=article.id,
            )[0]
            announcement.notified_users.add(request.user)
            announcement.save()

            return {
                'redirect': reverse('news:article', args=(form.instance.id, ))
            }
    return {'form': form}

def sphinx_search_news(request):
    template = get_skin_template(request.user, 'includes/sphinx_search_news.html')
    if request.method == 'POST':
        form = SphinxSearchForm(request.POST)
        if form.is_valid():
            news = News.search.query(form.cleaned_data['query']).all()
            page = request.GET.get('page',1)
            _pages_ = get_settings(request.user, 'news_on_page', 20)
            news = paginate(news, page, pages=_pages_)
            return direct_to_template(request, template,
                {'form': form, 'news': news, 'query': form.cleaned_data['query']})
        else:
            return direct_to_template(request, template,
                {'form': form, 'query': form.cleaned_data['query']})
    form = SphinxSearchForm()
    return direct_to_template(request, template,
        {'form': form})

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

@has_permission('news.can_edit')
@login_required_json
@render_to('news/article.html')
def article_status_set(request, pk):
    article = get_object_or_404(News, pk=pk)
    form = ArticleStatusForm(request.POST or None, instance=article)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return {
                'redirect': 'news:article',
                'redirect-args': (form.instance.pk, )
            }
    return {'form': form}


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


class EventView(EventPermissionMixin, generic.DetailView):
    model = Event
    template_name = 'events/event.html'


class EventUpdateView(EventPermissionMixin, generic.UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_form.html'


class EventDeleteView(EventPermissionMixin, generic.DeleteView):
    model = Event
    form_class = EventForm
    template_name = 'events/event_confirm_delete.html'
    success_url = reverse_lazy('news:events')