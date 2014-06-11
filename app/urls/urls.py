from django.conf.urls import url, include, patterns
from apps.core.shortcuts import direct_to_template
from django.contrib import admin
admin.autodiscover()

from django.conf import settings
from apps.core.feeds import *

urlpatterns = patterns(
    '',
    url(r'^grappelli/', include('grappelli.urls')),
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', admin.site.urls),
    (r'^you/should/fulfil/your/destiny/$', direct_to_template,
        {'template': 'get_a_working_browser.html', }),

    url(r'^feeds/news/$', NewsEntries(), name='feed-news'),
    url(r'^feeds/news/atom/$', AtomNewsEntries(), name='feed-news-atom'),
    (r'^json/', include('apps.jsonapp.urls', namespace='json')),
    (r'^', include('apps.accounts.urls', namespace='accounts')),
    (r'^', include('apps.core.urls', namespace='core')),
    (r'^', include('apps.wh.urls', namespace='wh')),
    (r'^', include('apps.files.urls', namespace='files')),
    (r'^', include('apps.news.urls', namespace='news')),
    (r'^', include('apps.tabletop.urls', namespace='tabletop')),
    (r'^', include('apps.karma.urls', namespace='karma')),
    (r'^', include('apps.comments.urls', namespace='comments')),
    (r'^forum/', include('apps.pybb.urls', namespace='pybb')),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)


if settings.DEV_SERVER:
    urlpatterns += patterns(
        '',
        url(r'^uploads/(?P<path>.*)$', 'django.views.static.serve',
            {
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True
            }),
    )
