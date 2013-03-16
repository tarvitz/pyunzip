from django.conf.urls.defaults import *
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

urlpatterns = patterns('apps.whadmin.views',
    (r'^$','index'),
    (r'^user/creation/$','user_creation'),
    (r'^rangs/$', 'rangs'),
)


