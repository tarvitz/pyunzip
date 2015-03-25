# coding: utf-8
from django.contrib.auth import get_user_model
User = get_user_model()
from apps.comments.models import CommentWatch
from apps.news.models import Event
from apps.core.tests import (
    TestHelperMixin, ApiAnonymousUserTestCaseMixin, ApiAdminUserTestCaseMixin,
    ApiUserOwnerTestCaseMixin, ApiUserNotOwnerTestCaseMixin,
    ApiRestrictedAnonymousUserTestCaseMixin,
    ApiRestrictedOwnerUserTestCaseMixin,
    ApiRestrictedUserNotOwnerTestCaseMixin,
)
from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse

from apps.core.helpers import get_content_type
import simplejson as json
from copy import deepcopy

__all__ = ['CommentWatchViewSetTest', 'CommentWatchViewAnonymousUserTest',]


class CommentWatchViewMixin(object):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_event_places.json',
        'tests/fixtures/load_events.json',
        'tests/fixtures/load_comments.json',
        'tests/fixtures/load_comment_watches.json'
    ]

    model_class = CommentWatch
    pk_value = 1

    def setUp(self):
        self.event_ct = get_content_type(Event)
        # pk 13 in fixtures mean it should be Event content type
        CommentWatch.objects.filter(pk=13).update(content_type=self.event_ct)

        super(CommentWatchViewMixin, self).setUp()
        self.owner_field = 'user'

        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.event = Event.objects.get(pk=1)
        self.comment_watch = CommentWatch.objects.create(
            content_type=self.event_ct, object_pk=self.event.pk,
            comment=None, user=self.user,
        )

        self.url_detail = reverse(
            'api:commentwatch-detail', args=(self.comment_watch.pk, ))

        self.url_list = reverse('api:commentwatch-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'is_updated': True,
            'is_disabled': False,
            'content_type': reverse('api:contenttype-detail',
                                    args=(self.event_ct.pk, )),
            'user': reverse('api:user-detail', args=(self.user.pk, )),
            'object_pk': self.event.pk,
        }
        self.patch = {
            'is_updated': True,
        }
        self.post = {
            'content_type': reverse('api:contenttype-detail',
                        args=(self.event_ct.pk, )),
            'object_pk': self.event.pk,
            'user': self.admin.pk,
            'is_updated': False,
            'is_disabled': False,
        }
        self.object_detail_response = {
            'content_type': self.event_ct.pk,
            'id': 5,
            'is_disabled': False,
            'is_updated': False,
            'object_pk': 1,
            'url': '/events/1/',
            'user': 6
        }


class CommentWatchViewAnonymousUserTest(CommentWatchViewMixin,
                                        ApiRestrictedAnonymousUserTestCaseMixin,
                                        APITestCase):
    pass


class CommentWatchViewAdminUserTest(CommentWatchViewMixin,
                                    ApiAdminUserTestCaseMixin,
                                    APITestCase):
    pass


class CommentWatchViewUserTest(CommentWatchViewMixin,
                               ApiRestrictedOwnerUserTestCaseMixin,
                               APITestCase):
    pass


class CommentWatchViewUserNotOwnerTest(CommentWatchViewMixin,
                                       ApiRestrictedUserNotOwnerTestCaseMixin,
                                       APITestCase):
    pass


class CommentWatchViewSetTest(TestHelperMixin, APITestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_event_places.json',
        'tests/fixtures/load_events.json',
        'tests/fixtures/load_comments.json',
    ]

    def setUp(self):
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.event_ct = get_content_type(Event)
        self.event = Event.objects.get(pk=1)
        self.comment_watch = CommentWatch.objects.create(
            content_type=self.event_ct, object_pk=self.event.pk,
            comment=None, user=self.user,
        )

        self.url_detail = reverse(
            'api:commentwatch-detail', args=(self.comment_watch.pk, ))

        self.url_list = reverse('api:commentwatch-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'id': self.comment_watch.pk,
            'is_updated': True,
            'is_disabled': False,
            'content_type': self.event_ct.pk,
            'user': self.user.pk,
            'object_pk': self.comment_watch.pk,
        }
        self.patch = {
            'is_updated': True,
        }
        self.post = {
            'content_type': self.event_ct.pk,
            'object_pk': self.comment_watch.pk,
            'user': self.admin.pk,
            'is_updated': False,
            'is_disabled': False,
        }
        self.object_detail_response = {
            'id': 1, 'is_disabled': False, 'is_updated': False,
            'url': '/events/1/', 'content_type': 16, 'user': 6,
            'object_pk': 1,
        }

    # test anonymous user
    def test_anonymous_get_detail(self):
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_get_list(self):
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_put_detail(self):
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_post_list(self):
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_patch_detail(self):
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

    def test_anonymous_delete_detail(self):
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'], 'Authentication credentials were not provided.')

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
        self.assertEqual(len(load['results']), CommentWatch.objects.count())

    def test_admin_put_detail(self):
        self.login('admin')
        count = CommentWatch.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = deepcopy(self.put)

        for field, item in put.items():
            self.assertEqual(load[field], put[field])
        self.assertEqual(CommentWatch.objects.count(), count)

    def test_admin_post_list(self):
        self.login('admin')
        count = CommentWatch.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(CommentWatch.objects.count(), count + 1)
        for field, value in post.items():
            self.assertEqual(load[field], post[field])

    def test_admin_patch_detail(self):
        self.login('admin')
        count = CommentWatch.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = CommentWatch.objects.get(pk=self.comment_watch.pk)
        for field, value in self.patch.items():
            self.assertEqual(getattr(obj, field), self.patch[field])
            self.assertEqual(load[field], self.patch[field])
        self.assertEqual(CommentWatch.objects.count(), count)

    def test_admin_delete_detail(self):
        self.login('admin')
        count = CommentWatch.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CommentWatch.objects.count(), count - 1)
    
    # test non-privileged user,
    # this user is owner of comment_watch so he/she can modify it and delete
    # also create new ones
    def test_user_get_detail(self):
        self.login('user')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, self.object_detail_response)

    def test_user_get_list(self):
        self.login('user')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            len(load['results']),
            CommentWatch.objects.filter(user=self.user).count()
        )

    def test_user_put_detail(self):
        self.login('user')
        count = CommentWatch.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = deepcopy(self.put)

        for field, item in put.items():
            self.assertEqual(load[field], put[field])
        self.assertEqual(CommentWatch.objects.count(), count)

    def test_user_post_list(self):
        self.login('user')
        count = CommentWatch.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(CommentWatch.objects.count(), count + 1)
        for field, value in post.items():
            self.assertEqual(load[field], post[field])

    def test_user_patch_detail(self):
        self.login('user')
        count = CommentWatch.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = CommentWatch.objects.get(pk=self.comment_watch.pk)
        for field, value in self.patch.items():
            self.assertEqual(getattr(obj, field), self.patch[field])
            self.assertEqual(load[field], self.patch[field])
        self.assertEqual(CommentWatch.objects.count(), count)

    def test_user_delete_detail(self):
        self.login('user')
        count = CommentWatch.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CommentWatch.objects.count(), count - 1)

    # test non-privileged user,
    # this user is not owner of represented comment watch
    # so he/she can not modify it and delete
    # but can create new  ones
    def test_not_owner_get_detail(self):
        self.login('user2')
        response = self.client.get(self.url_detail, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(load, {'detail': 'Not found'})

    def test_not_owner_get_list(self):
        self.login('user2')
        response = self.client.get(self.url_list, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            len(load['results']),
            CommentWatch.objects.filter(user=self.other_user).count())

    def test_not_owner_put_detail(self):
        self.login('user2')
        count = CommentWatch.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(CommentWatch.objects.count(), count)

    def test_not_owner_post_list(self):
        self.login('user2')
        count = CommentWatch.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(CommentWatch.objects.count(), count + 1)
        for field, value in post.items():
            self.assertEqual(load[field], post[field])

    def test_not_owner_patch_detail(self):
        self.login('user2')
        count = CommentWatch.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = CommentWatch.objects.get(pk=self.comment_watch.pk)
        for field, value in self.patch.items():
            self.assertNotEqual(getattr(obj, field), self.patch[field])
        self.assertEqual(CommentWatch.objects.count(), count)

    def test_not_owner_delete_detail(self):
        self.login('user2')
        count = CommentWatch.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(CommentWatch.objects.count(), count)