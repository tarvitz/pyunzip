# coding: utf-8

from apps.accounts.models import User
from apps.wh.models import Universe
from apps.core.tests import TestHelperMixin
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

import simplejson as json
import allure
from allure.constants import Severity


class UniverseViewSetTestMixin(object):
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

        self.universe = Universe.objects.get(pk="wh40k")
        self.url_detail = reverse(
            'api:universe-detail', args=(self.universe.pk, ))

        self.url_list = reverse('api:universe-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'title': 'Warhammer 40.000',
            'codename': self.universe.codename,  # primary key is not editable
        }
        self.patch = {
            'title': 'Dark Heresy',
        }
        self.post = {
            'title': 'Warhammer 40000 Dark Heresy',
            'codename': 'wh40kdh',
        }
        self.object_detail_response = {
            'title': 'Warhammer 40000',
            'codename': 'wh40k',
            'url': 'http://testserver/api/universes/wh40k/'
        }


@allure.feature('API: Universes')
class UniverseViewSetAnonymousUserTest(UniverseViewSetTestMixin,
                                       TestHelperMixin,
                                       APITestCase):
    def setUp(self):
        super(UniverseViewSetAnonymousUserTest, self).setUp()

    # test anonymous user
    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Universe.objects.count())

    @allure.story('put')
    @allure.severity(Severity.NORMAL)
    def test_put_detail(self):
        response = self.client.put(self.url_put, data=self.put, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list(self):
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_patch_detail(self):
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_delete_detail(self):
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], _('Authentication credentials were not provided.'))


@allure.feature('API: Universes')
class UniverseViewSetAdminUserTest(UniverseViewSetTestMixin, TestHelperMixin,
                                   APITestCase):
    # test admin user
    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        self.login('admin')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        self.login('admin')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Universe.objects.count())

    @allure.story('put')
    @allure.severity(Severity.NORMAL)
    def test_put_detail(self):
        self.login('admin')
        count = Universe.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        put = dict(**self.put)
        self.check_response(load, put)

        self.assertEqual(Universe.objects.count(), count)

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
    def test_post_list(self):
        """
        tabletop.change_universe permission holder users can freely assign
        owner to anyone, other users can only create universes for themselves

        :return:
        """
        self.login('admin')
        count = Universe.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = dict(**self.post)

        self.assertEqual(Universe.objects.count(), count + 1)
        self.check_response(load, post)

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
    def test_patch_detail(self):
        self.login('admin')
        count = Universe.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Universe.objects.get(pk=self.universe.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(Universe.objects.count(), count)

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_delete_detail(self):
        self.login('admin')
        count = Universe.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Universe.objects.count(), count - 1)


@allure.feature('API: Universes')
class UniverseViewSetUserTest(UniverseViewSetTestMixin, TestHelperMixin,
                              APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(UniverseViewSetUserTest, self).setUp()

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_detail(self):
        self.login('user')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_get_list(self):
        self.login('user')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Universe.objects.count())

    @allure.story('put')
    @allure.severity(Severity.NORMAL)
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

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
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

    @allure.story('post')
    @allure.severity(Severity.NORMAL)
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

    @allure.story('patch')
    @allure.severity(Severity.NORMAL)
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

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
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
