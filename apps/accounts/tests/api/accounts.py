# coding: utf-8

from apps.accounts.models import User
from apps.core.tests import (
    ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin
)
from tastypie.test import ResourceTestCase
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse


__all__ = [
    'UserResourceTest', 'UserViewSetAnonymousUserTest',
    'UserViewSetAdminUserTest', 'UserViewSetUserTest']


class UserResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['load_users.json']

    def setUp(self):
        super(UserResourceTest, self).setUp()


class UserViewSetMixin(object):
    fixtures = [
        'tests/fixtures/load_users.json',
    ]
    model_class = User
    pk_value = 6

    def setUp(self):
        super(UserViewSetMixin, self).setUp()
        self.user = User.objects.get(username='user')

        self.url_detail = reverse('api:user-detail', args=(self.user.pk, ))
        self.url_put = reverse('api:user-detail', args=(self.user.pk, ))
        self.url_patch = reverse('api:user-detail', args=(self.user.pk, ))
        self.url_delete = reverse('api:user-detail', args=(self.user.pk, ))
        self.url_post = reverse('api:user-list')
        self.url_list = reverse('api:user-list')

        self.object_detail_response = {
            'username': 'user', 'gender': 'n', 'is_active': True,
            'avatar': '', 'nickname': 'user',
            'date_joined': '2013-03-18T04:39:07.267',
            'email': 'user@blacklibrary.ru',
            'id': 6
        }
        self.object_admin_detail_response = {
            'about': '',
            'army': None,
            'avatar': '',
            'date_joined': '2013-03-18T04:39:07.267',
            'email': 'user@blacklibrary.ru',
            'first_name': '',
            'gender': 'n',
            'groups': [],
            'is_active': True,
            'is_staff': False,
            'is_superuser': False,
            'jid': None,
            'karma': 0,
            'last_login': '2013-03-18T04:39:07.267',
            'last_name': '',
            'nickname': 'user',
            'photo': '',
            'plain_avatar': '',
            'ranks': [],
            'settings': None,
            'tz': 0.0,
            'uin': None,
            'url': 'http://testserver/api/users/6/',
            'user_permissions': [],
            'username': 'user'
        }

        self.patch = {
            'username': 'patched_user',
            'nickname': 'butcher',
        }

        self.put = {
            'username': 'new_username',
            'nickname': 'man',
            'gender': 'm',
            'email': 'new_uer@blacklibrary.ru',
        }
        self.post = {
            'username': 'new_username',
            'nickname': 'man',
            'gender': 'm',
            'email': 'new_uer@blacklibrary.ru',
        }


class UserViewSetAnonymousUserTest(UserViewSetMixin,
                                   ApiAnonymousUserTestCaseMixin,
                                   APITestCase):
    pass


class UserViewSetAdminUserTest(UserViewSetMixin,
                               ApiAdminUserTestCaseMixin,
                               APITestCase):
    pass


class UserViewSetUserTest(UserViewSetMixin,
                          ApiAnonymousUserTestCaseMixin,
                          APITestCase):
    pass