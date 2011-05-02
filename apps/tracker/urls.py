from django.conf.urls.defaults import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.vote.views',
    url('xhr/mark/read/(?P<app_n_model>[\w.]+)/(?P<id>\d+)/$','mark_read',
        name='xhr_mark_read'),
)


