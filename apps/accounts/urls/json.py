from django.conf.urls import patterns, include, url

urlpatterns = patterns('apps.accounts.views.json',
    url(r'^users/$', 'users', name='users'),
    url(r'^specs/(?P<pk>\d+)/patterns/$', 'spec_patterns',
        name='spec-patterns')
)
