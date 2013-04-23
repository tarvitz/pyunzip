#from django.conf.urls.defaults import *
from django.conf.urls import *
from django.conf import settings
from apps.core.helpers import direct_to_template
from django.shortcuts import redirect
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
    url(r'static/(?P<path>.*)$', 'django.views.static.serve',
            {
                'document_root': settings.STATIC_ROOT,
                'show_indexes': True,
            }
        ),

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
    (r'^json/', include('apps.jsonapp.urls', namespace='json')),
    (r'^', include('apps.core.urls', namespace='core')),
    (r'^', include('apps.wh.urls', namespace='wh')),
    (r'^', include('apps.files.urls', namespace='files')),
    (r'^', include('apps.news.urls', namespace='news')),
    (r'^', include('apps.tabletop.urls', namespace='tabletop')),
    (r'^', include('apps.vote.urls', namespace='vote')),
    (r'^', include('apps.karma.urls', namespace='karma')),
    (r'^', include('apps.farseer.urls', namespace='farseer')),
    (r'^', include('apps.tracker.urls', namespace='tracker')),
    (r'^forum/',include('apps.pybb.urls')),
    (r'^devblog/', include('apps.blogs.urls', namespace='blog')),
    (r'^whadmin/', include('apps.whadmin.urls')),
    (r'^test/test/$', direct_to_template,{'template': 'test.html'}), 
    #(r'^quotes/',include('apps.quotes.urls')),
    #(r'^sitemap.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    #(r'^rules/$', direct_to_template,
    #    {'template':'codex.html'})
    #
)
urlpatterns += patterns('',
    ('^', include('django.contrib.flatpages.urls')),
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
