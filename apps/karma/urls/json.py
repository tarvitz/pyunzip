from django.conf.urls import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.karma.views.json',
    url('status/(?P<codename>[\w\s-]+)/$',
        'karma_status',
        name='status'),
)
