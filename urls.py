from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template,redirect_to
from django.utils.translation import ugettext_lazy as _
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from apps.core.feeds import *
from django.contrib.sites.models import Site

urlpatterns = patterns('',
    # Example:
    # (r'^warmist/', include('warmist.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    url(r'^grappelli/', include('grappelli.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', admin.site.urls),
    (r'^you/should/fulfil/your/destiny/$', direct_to_template,
        {'template': 'get_a_working_browser.html',}),

#    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed',
#        {'feed_dict': feeds}),
#    url('^feeds/?P<url>.*/$', 'django.contrib.syndication.views.feed',
#        {'feed_dict': feeds}, name='warmist_feed'),
   # (r'^search/$', direct_to_template,
   #     {'template': 'search_iframe.html'}),
    url(r'^feeds/news/$', NewsEntries(), name='feed-news'),
    url(r'^feeds/news/atom/$', AtomNewsEntries(), name='feed-news-atom'),
    (r'^', include('apps.core.urls')),
    (r'^', include('apps.wh.urls')),
    (r'^', include('apps.files.urls')),
    (r'^', include('apps.news.urls')),
    (r'^', include('apps.tabletop.urls')),
    (r'^', include('apps.vote.urls')),
    (r'^', include('apps.karma.urls')),
    (r'^', include('apps.farseer.urls')),
    (r'^', include('apps.tracker.urls')),
    (r'^forum/',include('apps.pybb.urls')),
    (r'^devblog/', include('apps.blogs.urls')),
    (r'^whadmin/', include('apps.whadmin.urls')),
    (r'^test/test/$', direct_to_template,{'template': 'test.html'}), 
    #(r'^quotes/',include('apps.quotes.urls')),
    #(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    #(r'^rules/$', direct_to_template,
    #    {'template':'codex.html'})
    #
)

if settings.DEV_SERVER:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root': settings.MEDIA_ROOT ,
                'show_indexes': True,
                }),
        (r'^styles/(?P<path>.*)$', 'django.views.static.serve',
                {'document_root':settings.STYLES_ROOT,
                    'show_indexes': True,
                }),
        (r'^admin_media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.ADMIN_MEDIA,
            'show_indexes': True,
            }
        ),
        url(r'static/(?P<path>.*)$', 'django.views.static.serve',
            {
                'document_root': settings.STATIC_ROOT,
                'show_indexes': True,
            }
        ),

    )
