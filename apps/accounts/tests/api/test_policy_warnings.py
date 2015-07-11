# coding: utf-8

from django.contrib.auth import get_user_model
User = get_user_model()

from apps.accounts.models import PolicyWarning

from apps.core.tests import TestHelperMixin
from rest_framework import status
from rest_framework.test import APITestCase

from django.conf import settings
from django.db.models import Q
from django.core.urlresolvers import reverse
from datetime import datetime, date, timedelta
from django.utils.translation import ugettext_lazy as _

import simplejson as json


__all__ = [
    'PolicyWarningViewSetAdminUserTest',
    'PolicyWarningViewSetAnonymousUserTest',
    'PolicyWarningViewSetTestMixin',
    'PolicyWarningViewSetUserTest'
]


class PolicyWarningViewSetTestMixin(object):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_policy_warnings.json',
    ]

    def setUp(self):
        self.maxDiff = None
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.policy_warning = PolicyWarning.objects.get(pk=1)

        self.url_detail = reverse(
            'api:policywarning-detail', args=(self.policy_warning.pk, ))

        self.url_list = reverse('api:policywarning-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'id': self.policy_warning.pk,
            'comment': u'Comment behaviour!',
            'date_expired': date(
                *(datetime.now() + timedelta(weeks=1)).timetuple()[:3]),
            'is_expired': False,
            'level': 2,
            'user': reverse('api:user-detail', args=(self.user.pk, ))
        }
        self.patch = {
            'level': settings.READONLY_LEVEL,
        }
        self.post = {
            'comment': u'Spammish behaviour!',
            'date_expired': date(
                *(datetime.now() + timedelta(weeks=2)).timetuple()[:3]),
            'is_expired': False,
            'level': 4,
            'user': reverse('api:user-detail', args=(self.user.pk, ))
        }
        self.object_detail_response = {
            'comment': u'\u044b!',
            'created_on': '2014-06-10T14:36:21.760000',
            'date_expired': '2014-06-10',
            'is_expired': False,
            'level': 4,
            'updated_on': '2014-06-10T14:34:15.770000',
            'url': 'http://testserver/api/warnings/1/',
            'user': 'http://testserver/api/users/2/'
        }


class PolicyWarningViewSetAnonymousUserTest(PolicyWarningViewSetTestMixin,
                                            TestHelperMixin, APITestCase):
    def setUp(self):
        super(PolicyWarningViewSetAnonymousUserTest, self).setUp()

    # test anonymous user
    def test_get_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(
            {'detail': _('Authentication credentials were not provided.')},
            load
        )

    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load,
            {'detail': _('Authentication credentials were not provided.')})

    def test_put_detail(self):
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
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


class PolicyWarningViewSetAdminUserTest(PolicyWarningViewSetTestMixin,
                                        TestHelperMixin, APITestCase):
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
        self.assertEqual(len(load['results']), PolicyWarning.objects.count())

    def test_put_detail(self):
        self.login('admin')
        count = PolicyWarning.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = dict(**self.put)
        put.pop('id')
        self.check_response(load, put)

        self.assertEqual(PolicyWarning.objects.count(), count)

    def test_post_list(self):
        """
        accounts.change_policy_warning permission holder users can freely
        assign sender to anyone, other users can only create policy_warnings
        for themselves

        :return:
        """
        self.login('admin')
        count = PolicyWarning.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = dict(**self.post)

        self.assertEqual(PolicyWarning.objects.count(), count + 1)
        self.check_response(load, post)

    def test_patch_detail(self):
        self.login('admin')
        count = PolicyWarning.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = PolicyWarning.objects.get(pk=self.policy_warning.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(PolicyWarning.objects.count(), count)

    def test_delete_detail(self):
        self.login('admin')
        count = PolicyWarning.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PolicyWarning.objects.count(), count - 1)


class PolicyWarningViewSetUserTest(PolicyWarningViewSetTestMixin,
                                   TestHelperMixin, APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(PolicyWarningViewSetUserTest, self).setUp()

    def test_get_detail(self):
        """Anyone except sender, addressee would retrieve 404"""
        self.login('user')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_detail_not_self(self):
        """
        tests for retrieve warning which is not belong to this user
        :return:
        """
        self.policy_warning.user = self.other_user
        self.policy_warning.save()
        self.login('user')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, {'detail': _('Not found.')})

    def test_get_list(self):
        self.login('user')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        qset = Q(user=self.user)
        self.assertEqual(len(load['results']),
                         PolicyWarning.objects.filter(qset).count())

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
        """
        any user can create his own policy_warning, whatever user would post
        the owner by default is bind for his/hers id

        :return:
        """
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
