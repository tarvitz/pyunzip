from django.conf.urls import *
from apps.core.shortcuts import direct_to_template
from django.contrib.auth.decorators import login_required
from apps.news import views


urlpatterns = patterns(
    'apps.news.views',
    url('^$', views.NewsListView.as_view(), name='index'),
    url(r'^news/(?P<pk>\d+)/$', views.NewsDetail.as_view(), name='article'),
    url(r'^news/(?P<pk>\d+)/edit/$', views.NewsUpdateView.as_view(),
        name='news-update'),
    url(r'^news/user/$', 'news_user', name='news-user'),
    url(r'^article/edit/(?P<id>\d+)/$','add_article', {'edit_flag':'True'},
        name='article-edit'),
    url('^markup/preview/$', 'markup_preview', name='markup-preview'),
    url(r'article/created/$', direct_to_template,
        {'template': 'news/article_created.html'},
        name='article-created'),
    # CBV
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
        name='event-delete'),
    url(r'^events/(?P<pk>\d+)/join/$',
        login_required(views.EventParticipateView.as_view()),
        name='event-join')
)