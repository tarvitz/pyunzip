from django.conf.urls.defaults import *
from apps.news import views

urlpatterns = patterns('apps.news.views', 
    url(r'^$','news', name='index'),
    url(r'^news/(?P<approved>(unapproved|approved))/$', 'news', name='news'), #this is somekind of brainfuck!
    url(r'^news/$', views.news, name='news'),
    #url(r'^news/$', 'news', name='news'),
    url(r'^news/archived/$','archived_news', name='archived-news'),
    url(r'^archived/article/(?P<id>\d+)/$','show_archived_article', name='article-archived'),
    url(r'^news/(?P<category>[\w\s]+)/$', 'news', name='news'),
    #(r'^news/(?P<page>)/$', 'news' ),
    url(r'^news/article/(?P<number>\d+)/$', 'show_article', {'object_model':'news.news'},
        name='article'),
    url(r'^article/(?P<number>\d+)/$', 'show_article', {'object_model':'news.news'}),
    #(r'^article/add/$', 'add_article'),
    url(r'^article/add/$', 'action_article',
        name='article-add'),
    #url('^meatings/$', 'view_meatings',
    #    name='view_meatings'),
    #url('^meatings/(?P<id>\d+)/$', 'view_meating',
    #    name='view_meatings'),
    #url('^meatings/add/$', 'add_meating',
    #    name='add_meating'),
    url(r'^article/edit/(?P<id>\d+)/$', 'action_article',
        {'action': 'edit'},
        name='article-edit'),
    url(r'^article/edit/(?P<id>\d+)/$','add_article', {'edit_flag':'True'},
        name='article-edit'),
    url(r'^article/(?P<id>\d+)/(?P<action>(approve|unapprove|delete))/$', 'article_action',
        name='article-action'),
    url(r'^article/(?P<id>\d+)/delete/$', 'article_action', {'action': 'delete'},
        name='article-delete'),
    #moved to apps.core.urls and apps.core.views
    #url('^comment/edit/(?P<id>\d+)/$', 'edit_comment',
    #    name='edit_comment'),
    url(r'^sphinx/news/$', 'sphinx_search_news', name='news-sph'),
    url('^comment/preview/$', 'comment_preview', name='comment-preview'),
)
