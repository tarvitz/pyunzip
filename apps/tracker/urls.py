from django.conf.urls.defaults import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.tracker.views',
    url('^xhr/mark/read/$', 'xhr_mark_read', { 'app_n_model': 'None.None', 'id': 0 },
        name='xhr_mark_read'),
    url('^xhr/mark/read/(?P<app_n_model>[\w.]+)/(?P<id>\d+)/$','xhr_mark_read',
        name='xhr_mark_read'),
)

