# coding: utf-8

from apps.accounts.models import User
from apps.core.tests import (
    ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin
)
from rest_framework.test import APITestCase
from django.core.urlresolvers import reverse


__all__ = [
    'UserViewSetAnonymousUserTest', 'UserViewSetAdminUserTest',
    'UserViewSetUserTest']


class UserViewSetMixin(object):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
    ]
    model_class = User
    pk_value = 2

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
            'username': 'user',
            'gender': 'm',
            'is_active': True,
            'avatar': 'http://testserver/uploads/avatars/1_user_WviM94D.png',
            'nickname': 'user',
            'date_joined': '2015-07-08T22:42:15.379000',
            'id': 2
        }
        self.object_admin_detail_response = {
            'about': 'admin all mighty universe',
            'army': 'http://testserver/api/armies/2/',
            'avatar': 'http://testserver/uploads/avatars/1_user_WviM94D.png',
            'date_joined': '2015-07-08T22:42:15.379000',
            'birthday': None,
            'email': 'user@blacklibrary.ru',
            'first_name': 'User',
            'gender': 'm',
            'groups': [],
            'is_active': True,
            'is_staff': True,
            'is_superuser': False,
            'jid': 'user@blacklibrary.ru',
            'karma': 0,
            'last_login': '2015-07-08T22:42:23.051000',
            'last_name': 'User',
            'nickname': 'user',
            'photo': None,
            'plain_avatar': None,
            'ranks': [],
            'settings': None,
            'tz': 0.0,
            'uin': 0,
            'url': 'http://testserver/api/users/2/',
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
