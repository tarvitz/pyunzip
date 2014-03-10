from django.conf.urls import patterns, include, url
from apps.accounts.resources import UserResource
from tastypie.api import Api

v1_api = Api()
v1_api.register(UserResource())

urlpatterns = patterns(
    '',
    url(r'^api/', include(v1_api.urls)),
)
