from django.conf.urls import *
from apps.core.shortcuts import direct_to_template
from django.contrib.auth.decorators import login_required
from apps.news import views
from apps.news.views.rest import EventViewSet

from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'events', EventViewSet)

urlpatterns = patterns('apps.news.views',
    #url(r'^$', 'news', name='index'),
    url('^$', views.NewsListView.as_view(), name='index'),
    url(r'^news/(?P<pk>\d+)/$', views.NewsDetail.as_view(), name='article'),
    url(r'^news/(?P<approved>(unapproved|approved))/$', 'news', name='news'), #this is somekind of brainfuck!
    url(r'^news/$', views.NewsListView.as_view(), name='news'),
    url(r'^news/(?P<pk>\d+)/edit/$', views.NewsUpdateView.as_view(),
        name='news-update'),
    url(r'^news/user/$', 'news_user', name='news-user'),
    url(r'^news/archived/$','archived_news', name='archived-news'),
    url(r'^archived/article/(?P<id>\d+)/$','show_archived_article', name='article-archived'),
    url(r'^news/(?P<category>[\w\s\.\-_]+)/$', 'news', name='news'),
    url(r'^news/article/(?P<pk>\d+)/status/$', 'article_status_set',
        name='article-status-set'),
    url(r'^news/article/(?P<number>\d+)/$', 'article', {'object_model':'news.news'},
        name='article'),
    #url(r'^article/(?P<number>\d+)/$', 'article', {'object_model':'news.news'}),
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
    # cbv
    url(r'^calendar/$', direct_to_template,
        {'template': 'events/calendar.html'}, name='calendar'),
    url(r'^events/$', views.EventListView.as_view(), name='events'),
    url(r'^events/(?P<pk>\d+)/$', views.EventView.as_view(), name='event'),
    url(r'^events/create/$', login_required(views.EventCreateView.as_view()),
        name='event-create'),
    url(r'^events/(?P<pk>\d+)/update/$',
        login_required(views.EventUpdateView.as_view()),
        name='event-update'),
    url(r'^events/(?P<pk>\d+)/delete/$',
        login_required(views.EventDeleteView.as_view()),
        name='event-delete')
)

urlpatterns += patterns(
    '',
    url(r'^api/', include(router.urls)),
)