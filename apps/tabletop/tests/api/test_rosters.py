# coding: utf-8

from django.contrib.auth import get_user_model
User = get_user_model()
from apps.wh.models import Army, Side, Universe
from apps.tabletop.models import Roster, Codex
from apps.core.tests import TestHelperMixin
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse

from apps.core.helpers import get_content_type

import simplejson as json
from copy import deepcopy


class RosterViewSetTestMixin(object):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_sides.json',
        'load_armies.json',
        'load_codexes.json',
        'load_rosters.json',
    ]

    def setUp(self):
        self.side_ct = get_content_type(Side)
        self.army_ct = get_content_type(Army)
        # update content types
        Codex.objects.filter(content_type_id=17).update(
            content_type=self.side_ct)

        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.roster = Roster.objects.get(pk=1)
        self.codex = Codex.objects.get(pk=1)
        self.url_detail = reverse(
            'api:roster-detail', args=(self.roster.pk, ))

        self.url_list = reverse('api:roster-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'id': self.roster.pk,
            'owner': reverse('api:user-detail', args=(self.user.pk, )),
            'pts': 750,
            'roster': u'New 750pts roster',
            'revision': 4,
            'title': u'New mega Roster',
            'codex': reverse('api:codex-detail', args=(self.codex.pk, ))
            #'content': u'No newcomers are welcome',
        }
        self.patch = {
            'pts': 1250,
            'roster': u'New roster and so on',
            'codex': reverse('api:codex-detail', args=(2, ))
        }
        self.post = {
            # required: False
            'owner': reverse('api:user-detail', args=(self.user.pk, )),
            'pts': 555,
            'roster': u'New 555pts roster',
            'revision': 5,
            'title': u'New Roster',
            'codex': reverse('api:codex-detail', args=(self.codex.pk, ))
        }
        self.object_detail_response = {
            'codex': 'http://testserver/api/codexes/1/',
            'comments': '',
            'defeats': 0,
            'owner': 'http://testserver/api/users/6/',
            'pts': 1000,
            'revision': 5,
            'roster': u'\u0424\u041a, 2\u0422\u0430\u043a\u0442\u0438'
                      u'\u0447\u043a\u0438 \u0432 \u0440\u0438\u043d\u043e, '
                      u'\u0441\u043a\u0432\u0430\u0434 \u0442\u0435\u0440'
                      u'\u043c\u043e\u0432',
            'syntax': 'textile',
            'title': u'\u0422\u0435\u0441\u0442\u043e\u0432\u044b\u0439',
            'url': 'http://testserver/api/rosters/1/',
            'wins': 0
        }


class RosterViewSetAnonymousUserTest(RosterViewSetTestMixin, TestHelperMixin,
                                     APITestCase):
    def setUp(self):
        super(RosterViewSetAnonymousUserTest, self).setUp()

    # test anonymous user
    def test_get_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(
            load, {'detail': 'Authentication credentials were not provided.'})

    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load, {'detail': 'Authentication credentials were not provided.'})

    def test_put_detail(self):
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_post_list(self):
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_patch_detail(self):
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_delete_detail(self):
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')


class RosterViewSetAdminUserTest(RosterViewSetTestMixin, TestHelperMixin,
                                 APITestCase):
    # test admin user
    def test_admin_get_detail(self):
        self.login('admin')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_admin_get_list(self):
        self.login('admin')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Roster.objects.count())

    def test_admin_put_detail(self):
        self.login('admin')
        count = Roster.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = deepcopy(self.put)
        put.pop('id')
        self.check_response(load, put)

        self.assertEqual(Roster.objects.count(), count)

    def test_admin_post_list(self):
        """
        tabletop.change_roster permission holder users can freely assign
        owner to anyone, other users can only create rosters for themselves

        :return:
        """
        self.login('admin')
        count = Roster.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Roster.objects.count(), count + 1)
        self.check_response(load, post)

    def test_admin_patch_detail(self):
        self.login('admin')
        count = Roster.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Roster.objects.get(pk=self.roster.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(Roster.objects.count(), count)

    def test_admin_delete_detail(self):
        self.login('admin')
        count = Roster.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Roster.objects.count(), count - 1)


class RosterViewSetUserTest(RosterViewSetTestMixin, TestHelperMixin,
                            APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(RosterViewSetUserTest, self).setUp()

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
        self.assertEqual(len(load['results']), Roster.objects.count())

    def test_put_detail(self):
        self.login('user')
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        put = deepcopy(self.put)
        put.pop('id')
        self.check_response(load, put)

    def test_post_list(self):
        self.login('user')
        count = Roster.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Roster.objects.count(), count + 1)
        self.check_response(load, post)

    def test_post_list_no_owner(self):
        self.login('user')
        count = Roster.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Roster.objects.count(), count + 1)
        self.check_response(load, post)

    def test_patch_detail(self):
        self.login('user')
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Roster.objects.get(pk=self.roster.pk)
        self.check_instance(obj, load, self.patch)

    def test_delete_detail(self):
        self.login('user')
        count = Roster.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(Roster.objects.count(), count - 1)


class RosterViewSetUserNotOwnerTest(RosterViewSetTestMixin, TestHelperMixin,
                                    APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(RosterViewSetUserNotOwnerTest, self).setUp()

    def test_get_detail(self):
        self.login('user2')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_get_list(self):
        self.login('user2')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Roster.objects.count())

    def test_put_detail(self):
        self.login('user2')
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_post_list(self):
        """
        any user can create his own roster, whatever user would post
        the owner by default is bind for his/hers id

        :return:
        """
        self.login('user2')
        post = deepcopy(self.post)
        post.update({
            'owner': reverse('api:user-detail', args=(self.other_user.pk, ))
        })
        count = Roster.objects.count()
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(Roster.objects.count(), count + 1)
        self.check_response(load, post)

    def test_post_list_no_owner_set(self):
        """
        post without owner, as it default would be assign to current user
        :return:
        """
        self.login('user2')
        count = Roster.objects.count()
        post = deepcopy(self.post)
        post.pop('owner')
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        self.assertEqual(Roster.objects.count(), count + 1)
        self.check_response(load, post)
        roster = Roster.objects.latest('id')
        self.assertEqual(roster.owner, self.other_user)

    def test_patch_detail(self):
        self.login('user2')
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_delete_detail(self):
        self.login('user2')
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')