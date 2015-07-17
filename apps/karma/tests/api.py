# coding: utf-8

from django.contrib.auth import get_user_model
User = get_user_model()

from apps.karma.models import Karma
from apps.karma.serializers import FAILURE_MESSAGES
from apps.core.tests import TestHelperMixin

from rest_framework import status
from rest_framework.test import APITestCase

from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text
from django.core.urlresolvers import reverse
from django.conf import settings

import simplejson as json
from copy import deepcopy

__all__ = [
    'KarmaViewSetAdminUserTest', 'KarmaViewSetAnonymousUserTest',
    'KarmaViewSetTestMixin',
    'KarmaViewSetUserTest'
]


class KarmaViewSetTestMixin(object):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_karma.json',
    ]

    def setUp(self):
        self.maxDiff = None
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.karma = Karma.objects.get(pk=1)

        self.url_detail = reverse(
            'api:karma-detail', args=(self.karma.pk, ))

        self.url_list = reverse('api:karma-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'id': self.karma.pk,
            'comment': u'new comment',
            'url': 'http://testserver/api/karmas/1/',
            'value': 1,
            'voter': reverse('api:user-detail', args=(self.user.pk, )),
            'user': reverse('api:user-detail', args=(self.other_user.pk, )),
        }

        self.patch = {
            'comment': u'Altered comment',
        }
        self.post = {
            'comment': u'\u0442\u0443\u0442 =)',
            'url': 'http://testserver/api/karmas/2/',
            'user': reverse('api:user-detail', args=(self.other_user.pk, )),
            'voter': reverse('api:user-detail', args=(self.user.pk, )),
            'value': 1,
        }
        self.object_detail_response = {
            'comment': u'\u0442\u0443\u0442 =)',
            'date': '2013-04-08T01:48:58.795000',
            'site_url': '/news/4/',
            'url': '/api/karmas/1/',
            'user': 'http://testserver/api/users/1/',
            'value': -5,
            'voter': 'http://testserver/api/users/2/'
        }


class KarmaViewSetAnonymousUserTest(KarmaViewSetTestMixin, TestHelperMixin,
                                    APITestCase):
    def setUp(self):
        super(KarmaViewSetAnonymousUserTest, self).setUp()

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
        self.assertEqual(len(load['results']), Karma.objects.count())

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


class KarmaViewSetAdminUserTest(KarmaViewSetTestMixin, TestHelperMixin,
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
        self.assertEqual(len(load['results']), Karma.objects.count())

    def test_put_detail(self):
        self.login('admin')
        count = Karma.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = deepcopy(self.put)
        put.pop('id')
        self.check_response(load, put)

        self.assertEqual(Karma.objects.count(), count)

    def test_post_list(self):
        """
        accounts.change_karma permission holder users can freely assign
        sender to anyone, other users can only create karmas for themselves

        :return:
        """
        self.login('admin')
        count = Karma.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Karma.objects.count(), count + 1)
        self.check_response(load, post)

    def test_patch_detail(self):
        self.login('admin')
        count = Karma.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Karma.objects.get(pk=self.karma.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(Karma.objects.count(), count)

    def test_delete_detail(self):
        self.login('admin')
        count = Karma.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Karma.objects.count(), count - 1)


class KarmaViewSetUserTest(KarmaViewSetTestMixin, TestHelperMixin,
                           APITestCase):
    # test non-privileged user,
    def setUp(self):
        super(KarmaViewSetUserTest, self).setUp()

    def test_get_detail(self):
        self.login('user')
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
        self.assertEqual(len(load['results']), Karma.objects.count())

    def test_put_detail(self):
        # forbidden for non privileged user, use: patch method instead
        self.login('user')
        put = deepcopy(self.put)
        count = Karma.objects.count()
        response = self.client.put(self.url_put, data=put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))

    def test_post_list(self):
        self.login('user')
        count = Karma.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        #self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Karma.objects.count(), count + 1)
        self.check_response(load, post)

    def test_post_list_failure(self):
        self.login('user')
        count = Karma.objects.count()
        post = deepcopy(self.post)
        post['voter'], post['user'] = post['user'], post['voter']
        post.update({
            'value': -2
        })
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(Karma.objects.count(), count)
        # user can not set karma for himself
        self.assertEqual(
            load['user'][0], force_text(FAILURE_MESSAGES['self_karma_set'])
        )
        # user can not set karma amount more than range: -1, 1
        self.assertEqual(
            load['value'][0],
            force_text(FAILURE_MESSAGES['karma_amount_exceed'])
        )
        # user can not post karma alteration from other account
        self.assertEqual(
            load['voter'][0],
            force_text(FAILURE_MESSAGES['karma_voter_violation'])
        )

    def test_post_list_karma_timeout_exceed(self):
        """ non privileged users has limited karma create amount tries.
        it could be set with settings KARMA_PER_TIMEOUT_AMOUNT

        :return:
        """
        for item in range(settings.KARMA_PER_TIMEOUT_AMOUNT + 1):
            Karma.objects.create(
                user=self.other_user, voter=self.user, value=1,
                comment=u'new karma ' + str(item)
            )
        self.login('user')
        count = Karma.objects.count()
        post = deepcopy(self.post)

        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(Karma.objects.count(), count)

        self.assertEqual(
            load['non_field_errors'][0],
            force_text(FAILURE_MESSAGES['timeout'])
        )

    def test_patch_detail(self):
        self.login('user')
        count = Karma.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Karma.objects.get(pk=self.karma.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(Karma.objects.count(), count)

    def test_delete_detail(self):
        self.login('user')
        count = Karma.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Karma.objects.count(), count)
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            _('You do not have permission to perform this action.'))