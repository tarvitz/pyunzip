# coding: utf-8

from apps.accounts.models import User
from apps.core.tests import TestHelperMixin
from tastypie.test import ResourceTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse
import simplejson as json
from copy import deepcopy


class UserResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['load_users.json']

    def setUp(self):
        super(UserResourceTest, self).setUp()


class UserViewSetTest(TestHelperMixin, APITestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='user')

        self.url_detail = reverse('api:user-detail', args=(self.user.pk, ))
        self.url_put = reverse('api:user-detail', args=(self.user.pk, ))
        self.url_patch = reverse('api:user-detail', args=(self.user.pk, ))
        self.url_delete = reverse('api:user-detail', args=(self.user.pk, ))
        self.url_post = reverse('api:user-list')
        self.url_list = reverse('api:user-list')

        self.user_detail_response = {
            'username': 'user', 'gender': 'n', 'is_active': True,
            'avatar': '', 'nickname': 'user',
            'date_joined': '2013-03-18T04:39:07.267',
            'email': 'user@blacklibrary.ru',
            'id': 6
        }

        self.patch = {
            'username': 'patched_user',
            'nickname': 'butcher',
        }

        self.put = {
            'id': self.user.pk,
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

    # test anonymous user
    def test_anonymous_get_user_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_get_user_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_put_user_detail(self):
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_post_user_list(self):
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_patch_user_detail(self):
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_delete_user_detail(self):
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    # test admin user
    def test_admin_get_user_detail(self):
        self.login('admin')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.user_detail_response)

    def test_admin_get_user_list(self):
        self.login('admin')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), User.objects.count())

    def test_admin_put_user_detail(self):
        self.login('admin')
        count = User.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = deepcopy(self.put)

        for field, item in put.items():
            self.assertEqual(load[field], put[field])
        self.assertEqual(User.objects.count(), count)

    def test_admin_post_user_list(self):
        self.login('admin')
        count = User.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(User.objects.count(), count + 1)
        for field, value in post.items():
            self.assertEqual(load[field], post[field])

    def test_admin_patch_user_detail(self):
        self.login('admin')
        count = User.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        user = User.objects.get(pk=self.user.pk)
        for field, value in self.patch.items():
            self.assertEqual(getattr(user, field), self.patch[field])
            self.assertEqual(load[field], self.patch[field])
        self.assertEqual(User.objects.count(), count)

    def test_admin_delete_user_detail(self):
        self.login('admin')
        count = User.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), count - 1)
    
    # test non-privileged user
    def test_user_get_user_detail(self):
        self.login('user')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.user_detail_response)

    def test_user_get_user_list(self):
        """
        user could retrieve only self's data

        :return:
        """
        self.login('user')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            len(load['results']),
            User.objects.filter(pk=self.user.pk).count()
        )

    def test_user_put_user_detail(self):
        self.login('user')
        count = User.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_user_post_user_list(self):
        self.login('user')
        count = User.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_user_patch_user_detail(self):
        self.login('user')
        count = User.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_user_delete_user_detail(self):
        self.login('user')
        count = User.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')
        self.assertEqual(User.objects.count(), count)