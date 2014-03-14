from django.conf.urls import *

from apps.pybb import views
from apps.pybb.feeds import LastPosts, LastTopics
from django.contrib.auth.decorators import login_required

feeds = {
    'posts': LastPosts,
    'topics': LastTopics,
}
urlpatterns = patterns(
    url('^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
        {'feed_dict': feeds}, name='feed'),

)
urlpatterns += patterns('',
    # Misc
    url('^$', views.index, name='index'),
    url('^category/(?P<category_id>\d+)/$', views.show_category,
        name='category'),
    url('^forum/(?P<forum_id>\d+)/$', views.show_forum,
        name='forum'),
    # User
    url('^user/(?P<username>.*)/$', views.user, name='profile'),
    #url('^profile/edit/$', views.edit_profile, name='profile-edit'),
    #url('^users/$', views.users, name='users'),

    # Topic
    url('^topic/(?P<topic_id>\d+)/$', views.show_topic,
        name='topic'),
    url('^topics/(?P<pk>\d+)/posts/$', views.PostListView.as_view(),
        name='posts'),
    #url('^forum/(?P<forum_id>\d+)/topic/add/$', views.add_post,
    #    {'topic_id': None}, name='topic-add'),
    url('^forums/(?P<pk>\d+)/topics/add/$',
        login_required(views.PostAddView.as_view()),
        {'topic': True},
        name='topic-add'),
    url('^topic/(?P<topic_id>\d+)/stick/$', views.stick_topic,
        name='topic-stick'),
    url('^topic/(?P<topic_id>\d+)/unstick/$', views.unstick_topic,
        name='topic-unstick'),
    url('^topic/(?P<topic_id>\d+)/close/$', views.close_topic,
        name='topic-close'),
    url('^topic/(?P<topic_id>\d+)/open/$', views.open_topic,
        name='topic-open'),

    # Post
    #url('^topic/(?P<topic_id>\d+)/post/add/$', views.add_post,
    #    {'forum_id': None}, name='post-add'),
    url('^topics/(?P<pk>\d+)/posts/add/$',
        login_required(views.PostAddView.as_view()), name='post-add'),
    url('^post/(?P<post_id>\d+)/$', views.show_post, name='post'),
    #url('^post/(?P<post_id>\d+)/edit/$', views.edit_post, name='post-edit'),
    url('^posts/(?P<pk>\d+)/edit/$',
        login_required(views.PostUpdateView.as_view()),
        name='post-edit'),
    url('^post/(?P<post_id>\d+)/delete/$', views.delete_post,
        name='post-delete'),

    # Subscription
    url('^subscription/topic/(?P<topic_id>\d+)/delete/$',
        views.delete_subscription, name='subscription-delete'),
    url('^subscription/topic/(?P<topic_id>\d+)/add/$',
        views.add_subscription, name='subscription-add'),

    # Themes
    url('^themes/(?P<theme>[\w\d]+)/switch/$', views.switch_theme,
        name='theme-switch'),
    # Polls
    url('^topic/(?P<pk>\d+)/poll/add/$', views.ManagePollView.as_view(),
        name='poll-add'),
    url('^poll/(?P<pk>\d+)/update/$', views.ManagePollView.as_view(),
        {'update': True},
        name='poll-update'),
    url('^poll/(?P<pk>\d+)/delete/$', views.ManagePollView.as_view(),
        {'delete': True},
        name='poll-delete'),
    url('^poll/(?P<pk>\d+)/configure/$', views.ConfigurePollView.as_view(),
        name='poll-configure'),
    url('^poll/(?P<pk>\d+)/vote/$', views.PollVoteView.as_view(),
        name='poll-vote'),
    #url('^topic/(?P<pk>\d+)/poll/add/step/(?P<step>.+)/$',
    #    views.add_poll_wizard, name='add-poll'),
)
