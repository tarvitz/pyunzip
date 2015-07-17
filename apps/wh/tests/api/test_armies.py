# coding: utf-8

from apps.accounts.models import User
from apps.wh.models import Army
from apps.core.tests import TestHelperMixin
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

import simplejson as json


class ArmyViewSetTestMixin(object):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_users.json',
    ]

    def setUp(self):
        self.maxDiff = None
        # update content types

        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.army = Army.objects.get(pk=1)
        self.url_detail = reverse(
            'api:army-detail', args=(self.army.pk, ))

        self.url_list = reverse('api:army-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'name': 'Dark Angels',
            'side': reverse('api:side-detail', args=(1, ))
        }
        self.patch = {
            'name': 'Ultra Marine',
        }
        self.post = {
            'name': 'Ultramarines',
            'side': reverse('api:side-detail', args=(1, ))
        }
        self.object_detail_response = {
            'name': 'Blood Ravens',
            'side':  'http://testserver/api/sides/1/',
            'url': 'http://testserver/api/armies/1/'
        }


class ArmyViewSetAnonymousUserTest(ArmyViewSetTestMixin, TestHelperMixin,
                                   APITestCase):
    def setUp(self):
        super(ArmyViewSetAnonymousUserTest, self).setUp()

    # test anonymous user
    def test_get_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load['count'], Army.objects.count())

    def test_put_detail(self):
        response = self.client.put(self.url_put, data=self.put, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))

    def test_post_list(self):
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))

    def test_patch_detail(self):
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))

    def test_delete_detail(self):
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))


class ArmyViewSetAdminUserTest(ArmyViewSetTestMixin, TestHelperMixin,
                               APITestCase):
    # test admin user
    def test_get_detail(self):
        self.login('admin')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_list(self):
        self.login('admin')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load['count'], Army.objects.count())

    def test_put_detail(self):
        self.login('admin')
        count = Army.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        put = dict(**self.put)
        self.check_response(load, put)

        self.assertEqual(Army.objects.count(), count)

    def test_post_list(self):
        self.login('admin')
        count = Army.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = dict(**self.post)

        self.assertEqual(Army.objects.count(), count + 1)
        self.check_response(load, post)

    def test_patch_detail(self):
        self.login('admin')
        count = Army.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Army.objects.get(pk=self.army.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(Army.objects.count(), count)

    def test_delete_detail(self):
        self.login('admin')
        count = Army.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Army.objects.count(), count - 1)


class ArmyViewSetUserTest(ArmyViewSetTestMixin, TestHelperMixin,
                          APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(ArmyViewSetUserTest, self).setUp()

    def test_get_detail(self):
        self.login('user')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_list(self):
        self.login('user')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load['count'], Army.objects.count())

    def test_put_detail(self):
        self.login('user')
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))

    def test_post_list(self):
        self.login('user')
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))

    def test_post_list_no_owner(self):
        self.login('user')
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))

    def test_patch_detail(self):
        self.login('user')
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))

    def test_delete_detail(self):
        self.login('user')
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))
