# Create your views here.
# ^^, coding: utf-8 ^^,
import os
from apps.news.models import News,Category,ArchivedNews, Meating
from apps.news.forms import ArticleForm, ArticleModelForm, AddMeatingForm
from apps.core.forms import CommentForm, SphinxSearchForm
from apps.files.models import Attachment
from apps.files.helpers import save_uploaded_file as save_file
from apps.core import make_links_from_pages as make_links
from apps.core import pages, get_skin_template
from apps.core.views import action_approve_simple
#deprecated
#from django.views.generic.simple import direct_to_template
#overriding
from apps.core.shortcuts import direct_to_template
from apps.core.forms import ApproveActionForm
#from apps.settings import MEDIA_ROOT
from django.conf import settings
from django.template import RequestContext,Template,Context
from django.contrib import auth
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import User,Permission
from django.utils.translation import ugettext_lazy as _
from django.core.paginator import InvalidPage, EmptyPage
#from apps.helpers.diggpaginator import DiggPaginator as Paginator
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseServerError, Http404
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment
from django.core import serializers
from django.core.urlresolvers import reverse
from datetime import datetime,timedelta
from os import stat
#filters
from apps.news.templatetags.newsfilters import spadvfilter,bbfilter, render_filter
from django.template.defaultfilters import striptags
from apps.tracker.decorators import user_visit
from apps.core.helpers import get_settings, paginate,can_act, handle_uploaded_file
from apps.core.decorators import benchmarking, update_subscription_new, has_permission
from apps.core.helpers import render_to, get_object_or_None
from apps.core import benchmark #processors

#def get_a_normal_browser(request):
#    agent = request.META['HTTP_USER_AGENT']
#    if 'msie 6.0' in agent.title().lower()\
#    or 'msie 7.0' in agent.title().lower():
#        return HttpResponseRedirect('you/should/fuifuill/your/destiny')

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
@benchmarking
def news(request, approved='approved', category=''):
    template = get_skin_template(request.user,'news.html')
    can_approve_news = None
    if request.user.is_authenticated():
        can_approve_news = request.user.user_permissions.filter(codename='edit_news')

    page = request.GET.get('page',1)

    #make an archives
    now = datetime.now()
    td = timedelta(days=365)
    older = now - td
    # TODO: move archiver to crontab
    all_news = News.objects.all()
    for n in all_news:
        if  older > n.date:
            n.archive()
    #TODO: DELETE duplicated code
    if request.user.is_superuser or can_approve_news:
        news = News.objects.all().order_by('-date').filter(category__name__icontains=category)
        if  approved == 'unapproved':
            news = News.objects.filter(approved__exact=False).order_by('-date')
            _pages_ = get_settings(request.user,'news_on_page',30)
            news = paginate(news,page,pages=_pages_)
            return render_to_response(template,{'news':news,'page':news},
                context_instance=RequestContext(request,processors=[benchmark]))

    else:
        news = News.objects.filter(approved=True)
        if request.user.is_authenticated():
            news = news | News.objects.filter(owner=request.user)

        news = news.order_by('-date')
    _pages_ = get_settings(request.user,'news_on_page',30)
    news = paginate(news,page,pages=_pages_,
        view='apps.news.views.news')
    return render_to_response(template,
        {'news': news,
        'page': news},
        context_instance=RequestContext(request,
            processors=[benchmark]))


def search_article(request):
    template = get_skin_template(request.user, "news/search.html")
    return render_to_response(template, {'form':''},
    context_instance=RequestContext(request))

@update_subscription_new(app_model='news.news', pk_field='number')
@user_visit(object_pk='number', ct='news.news')
@render_to('news/article.html')
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

    form = ArticleModelForm(
        request.POST or None, request=request, instance=instance
    )
    if request.method == 'POST':
        if form.is_valid():
            article = form.save(commit=False)
            article.owner = request.user
            article.save()
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
