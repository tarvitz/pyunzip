# coding: utf-8

from django.contrib.auth import get_user_model
User = get_user_model()
from apps.news.models import Event, EventPlace
from apps.core.tests import TestHelperMixin
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse

from apps.core.helpers import get_content_type

import simplejson as json
from copy import deepcopy
from datetime import datetime, timedelta


class EventViewSetTestMixin(object):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_event_places.json',
        'tests/fixtures/load_events.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.event_ct = get_content_type(Event)
        self.event_place = EventPlace.objects.get(pk=1)

        self.event = Event.objects.get(pk=1)
        self.url_detail = reverse(
            'api:event-detail', args=(self.event.pk, ))

        self.url_list = reverse('api:event-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'id': self.event.pk,
            'is_all_day': True,
            'is_finished': True,
            'type': 'game',
            'league': 'mtg',
            'place': 2,
            'date_start': datetime.now() + timedelta(minutes=10),
            'date_end': datetime.now() + timedelta(minutes=360),
            'title': u'Private',
            #'content': u'No newcomers are welcome',
        }
        self.patch = {
            'is_all_day': True,
            'type': 'tournament'
        }
        self.post = {
            'is_all_day': True,
            'is_finished': True,
            'type': 'order',
            'league': 'wh40k',
            'place': 2,
            'date_start': datetime.now() + timedelta(minutes=10),
            'date_end': datetime.now() + timedelta(minutes=720),
            'title': u'New Event',
            #'content': u'New event and so on',
        }
        self.object_detail_response = {
            'id': 1,
            'date_end': '2014-05-31T10:00:00',
            'date_start': '2014-05-31T12:00:00',
            'is_all_day': False,
            'is_finished': False,
            'is_new': True,
            'place': None,
            #'content': u'p. бухаем, не бухаем все дела dadasd',
            'league': 'wh40k',
            'title': u'Клевое событие',
            'type': 'order',
            'url': '/events/1/'
        }


class EventViewSetAnonymousUserTest(EventViewSetTestMixin, TestHelperMixin,
                                    APITestCase):
    def setUp(self):
        super(EventViewSetAnonymousUserTest, self).setUp()

    # test anonymous user
    def test_get_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)

        # Always False for anonymous user
        object_detail_response = deepcopy(self.object_detail_response)
        object_detail_response.update({
            'is_new': False
        })

        self.assertEqual(load, object_detail_response)

    def test_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(len(load['results']), Event.objects.count())

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


class EventViewSetAdminUserTest(EventViewSetTestMixin, TestHelperMixin,
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
        self.assertEqual(len(load['results']), Event.objects.count())

    def test_admin_put_detail(self):
        self.login('admin')
        count = Event.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = deepcopy(self.put)

        for field, item in put.items():
            if isinstance(item, (datetime, )):
                self.assertEqual(load[field], put[field].isoformat()[:-3])
            else:
                self.assertEqual(load[field], put[field])
        self.assertEqual(Event.objects.count(), count)

    def test_admin_post_list(self):
        self.login('admin')
        count = Event.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Event.objects.count(), count + 1)
        for field, value in post.items():
            if isinstance(value, (datetime, )):
                self.assertEqual(load[field], value.isoformat()[:-3])
            else:
                self.assertEqual(load[field], value)

    def test_admin_patch_detail(self):
        self.login('admin')
        count = Event.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Event.objects.get(pk=self.event.pk)
        for field, value in self.patch.items():
            if isinstance(getattr(obj, field), (datetime, )):
                self.assertEqual(getattr(obj, field).isoformat(), value)
            else:
                self.assertEqual(getattr(obj, field), value)
                self.assertEqual(load[field], value)
        self.assertEqual(Event.objects.count(), count)

    def test_admin_delete_detail(self):
        self.login('admin')
        count = Event.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), count - 1)


class EventViewSetUserTest(EventViewSetTestMixin, TestHelperMixin,
                           APITestCase):
    # test non-privileged user,
    # this user is owner of event so he/she can modify it and delete
    # also create new ones
    def setUp(self):
        super(EventViewSetUserTest, self).setUp()

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
        self.assertEqual(len(load['results']), Event.objects.count())

    def test_put_detail(self):
        self.login('user')
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_post_list(self):
        self.login('user')
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_patch_detail(self):
        self.login('user')
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_delete_detail(self):
        self.login('user')
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')
