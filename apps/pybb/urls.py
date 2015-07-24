from django.conf.urls import url, patterns

from apps.pybb.views import views
from apps.pybb.feeds import LastPosts, LastTopics
from django.contrib.auth.decorators import login_required

feeds = {
    'posts': LastPosts,
    'topics': LastTopics,
}

urlpatterns = patterns(
    '',
    # Misc
    url('^$', views.index, name='index'),
    url('^category/(?P<category_id>\d+)/$', views.show_category,
        name='category'),
    url('^forum/(?P<forum_id>\d+)/$', views.show_forum,
        name='forum'),
    # User
    url('^user/(?P<username>.*)/$', views.user, name='profile'),

    # Topic
    url('^topic/(?P<topic_id>\d+)/$', views.show_topic,
        name='topic'),
    url('^topics/(?P<pk>\d+)/posts/$', views.PostListView.as_view(),
        name='posts'),
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
    url('^topics/(?P<pk>\d+)/posts/add/$',
        login_required(views.PostAddView.as_view()), name='post-add'),
    url('^post/(?P<post_id>\d+)/$', views.show_post, name='post'),

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
    url('^themes/(?P<theme>[\w\d]+)/css/switch/$', views.switch_css_theme,
        name='css-theme-switch'),
    # Polls
    url('^topic/(?P<pk>\d+)/poll/add/$',
        login_required(views.ManagePollView.as_view()),
        name='poll-add'),
    url('^poll/(?P<pk>\d+)/update/$',
        login_required(views.ManagePollView.as_view()),
        {'update': True},
        name='poll-update'),
    url('^poll/(?P<pk>\d+)/delete/$',
        login_required(views.ManagePollView.as_view()),
        {'delete': True},
        name='poll-delete'),
    url('^poll/(?P<pk>\d+)/configure/$',
        login_required(views.ConfigurePollView.as_view()),
        name='poll-configure'),
    url('^poll/(?P<pk>\d+)/vote/$',
        login_required(views.PollVoteView.as_view()),
        name='poll-vote'),
)
