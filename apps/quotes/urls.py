from django.conf.urls.defaults import *

urlpatterns = patterns('apps.quotes.views',

    (r'^$', 'index'),
    (r'^pages/(?P<page_number>\d+)/$', 'index'),

    (r'^rss/$', 'rss'),
    (r'^top/$', 'best'),
    (r'^best/$', 'best'),
    (r'^quote/(?P<id>\d+)/$', 'quote'),
    (r'^vote/(?P<how>(up|down))/(?P<id>\d+)/$', 'vote'),
    (r'^add/$', 'add'),

    (r'^search/$', 'search'),
    (r'^search/pages/(?P<page_number>\d+)/$', 'search'),

    (r'queue/$', 'queue'),
    (r'queue/pages/(?P<page_number>\d+)/$', 'queue'),

    #(r'queue/', 'queue'),
    (r'queue/quote/(?P<id>\d+)/$', 'queue_quote'),
    (r'queue/quote/(?P<id>\d+)/approve/$', 'approve'),
    (r'queue/quote/(?P<id>\d+)/reject/$', 'reject'),
    (r'queue/quote/(?P<id>\d+)/hide/$', 'hide'),
    (r'queue/quote/(?P<id>\d+)/edit/$', 'edit'),

)
