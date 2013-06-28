from django.conf.urls import *
from apps.core.shortcuts import direct_to_template
from apps.news import views

urlpatterns = patterns('apps.news.views', 
    url(r'^$','news', name='index'),
    url(r'^news/(?P<approved>(unapproved|approved))/$', 'news', name='news'), #this is somekind of brainfuck!
    url(r'^news/$', views.news, name='news'),
    url(r'^news/user/$', 'news_user', name='news-user'),
    url(r'^news/archived/$','archived_news', name='archived-news'),
    url(r'^archived/article/(?P<id>\d+)/$','show_archived_article', name='article-archived'),
    url(r'^news/(?P<category>[\w\s\.\-_]+)/$', 'news', name='news'),
    url(r'^news/article/(?P<pk>\d+)/status/$', 'article_status_set',
        name='article-status-set'),
    url(r'^news/article/(?P<number>\d+)/$', 'article', {'object_model':'news.news'},
        name='article'),
    url(r'^article/(?P<number>\d+)/$', 'article', {'object_model':'news.news'}),
    url(r'^article/add/$', 'action_article',
        name='article-add'),
    url(r'^article/edit/(?P<id>\d+)/$', 'action_article',
        {'action': 'edit'},
        name='article-edit'),
    url(r'^article/edit/(?P<id>\d+)/$','add_article', {'edit_flag':'True'},
        name='article-edit'),
    url(r'^article/(?P<id>\d+)/(?P<action>(approve|unapprove|delete))/$', 'article_action',
        name='article-action'),
    url(r'^article/(?P<id>\d+)/delete/$', 'article_action', {'action': 'delete'},
        name='article-delete'),
    #url(r'^sphinx/news/$', 'sphinx_search_news', name='news-sph'),
    url('^markup/preview/$', 'markup_preview', name='markup-preview'),
    url(r'article/created/$', direct_to_template,
        {'template': 'news/article_created.html'},
        name='article-created'),
)
