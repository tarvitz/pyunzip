from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'template.views.home', name='home'),
    # url(r'^template/', include('template.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^', include('apps.wh.urls_json', namespace='wh')),
    #url(r'^', include('apps.core.urls_json', namespace='core')),
    #url(r'^', include('apps.news.urls_json', namespace='news')),
    url(r'^', include('apps.files.urls_json', namespace='files')),
    url(r'^', include('apps.tabletop.urls_json', namespace='tabletop')),
    url(r'^', include('apps.tracker.urls_json', namespace='tracker')),
)
