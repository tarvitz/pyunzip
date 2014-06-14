# coding: utf-8

from django.contrib.auth import get_user_model
User = get_user_model()

from apps.comments.models import Comment
from apps.news.models import Event

from apps.core.tests import TestHelperMixin
from apps.core.helpers import get_content_type
from rest_framework import status
from rest_framework.test import APITestCase

from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

import simplejson as json
from copy import deepcopy

__all__ = [
    'CommentViewSetAdminUserTest', 'CommentViewSetAnonymousUserTest',
    'CommentViewSetTestMixin', 'CommentViewSetUserNotOwnerTest',
    'CommentViewSetUserTest'
]


class CommentViewSetTestMixin(object):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_event_places.json',
        'tests/fixtures/load_events.json',
        'tests/fixtures/load_comments.json',
    ]

    def setUp(self):
        self.maxDiff = None
        self.event_ct = get_content_type(Event)
        self.event = Event.objects.get(pk=1)
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.other_user = User.objects.get(username='user2')

        self.comment = Comment.objects.get(pk=1)

        self.url_detail = reverse(
            'api:comment-detail', args=(self.comment.pk, ))

        self.url_list = reverse('api:comment-list')
        self.url_post = self.url_list
        self.url_put = self.url_detail
        self.url_patch = self.url_detail
        self.url_delete = self.url_detail

        self.put = {
            'id': self.comment.pk,
            'comment': u'put a comment here',
            'content_type': self.event_ct.pk,
            'object_pk': str(self.event.pk),
            'site': 1,  # RO
            'syntax': 'textile',
            'user': reverse('api:user-detail', args=(self.other_user.pk, ))
        }

        self.patch = {
            'comment': u'New comment comment and so on',
        }
        self.post = {
            'comment': u'here is new comment',
            'content_type': self.event_ct.pk,
            'object_pk': str(self.event.pk),
            'site': 1,
            'syntax': None,
            'user': reverse('api:user-detail', args=(self.user.pk, ))
        }
        self.object_detail_response = {
            "comment": u"\u0410 \u0432\u043e\u0442 \u0445\u0435\u0440!\n"
                       u"\u0422\u0435\u0441\u0442\u0438\u0440\u0443\u0435"
                       u"\u043c \u0442\u0435\u0441\u0442!\n\u0425\u0443"
                       u"\u044f\u043a!\n(spoiler)[test]!\n\n\u0420\u0410"
                       u"\u0417\u0420 \u0417!",
            "url": "http://testserver/api/comments/1/",
            "object_pk": "4",
            "site": 1,
            "syntax": "textile",
            "submit_date": "2013-02-03T04:43:52.440",
            "is_removed": False,
            "user": "http://testserver/api/users/6/",
            "content_type": 34,
            "is_public": True,
            "cache_comment": u"\t<p>\u0410 \u0432\u043e\u0442 "
                             u"\u0445\u0435\u0440!<br />\u0422\u0435\u0441"
                             u"\u0442\u0438\u0440\u0443\u0435\u043c "
                             u"\u0442\u0435\u0441\u0442!<br />\u0425\u0443"
                             u"\u044f\u043a!<br /><div class='spoiler_block'>"
                             u"<a href=\"#\" class='marker'>(+)</a><span "
                             u"class='text'> \u0441\u043f\u043e\u0439\u043b"
                             u"\u0435\u0440</span><div class='spoiler'>"
                             u"<div class='transparency tr_spoiler'></div>"
                             u"        test    </div></div>!</p>\n\n\t<p>"
                             u"\u0420\u0410\u0417\u0420 \u0417!</p>"
        }


class CommentViewSetAnonymousUserTest(CommentViewSetTestMixin, TestHelperMixin,
                                      APITestCase):
    def setUp(self):
        super(CommentViewSetAnonymousUserTest, self).setUp()

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
        self.assertEqual(len(load['results']), Comment.objects.count())

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


class CommentViewSetAdminUserTest(CommentViewSetTestMixin, TestHelperMixin,
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
        self.assertEqual(len(load['results']), Comment.objects.count())

    def test_put_detail(self):
        self.login('admin')
        count = Comment.objects.count()
        response = self.client.put(self.url_put, data=self.put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        put = deepcopy(self.put)
        put.pop('id')
        self.check_response(load, put)

        self.assertEqual(Comment.objects.count(), count)

    def test_post_list(self):
        """
        accounts.change_comment permission holder users can freely assign
        sender to anyone, other users can only create comments for themselves

        :return:
        """
        self.login('admin')
        count = Comment.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Comment.objects.count(), count + 1)
        self.check_response(load, post)

    def test_patch_detail(self):
        self.login('admin')
        count = Comment.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Comment.objects.get(pk=self.comment.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(Comment.objects.count(), count)

    def test_delete_detail(self):
        self.login('admin')
        count = Comment.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), count - 1)


class CommentViewSetUserTest(CommentViewSetTestMixin, TestHelperMixin,
                             APITestCase):
    # test non-privileged user,
    def setUp(self):
        super(CommentViewSetUserTest, self).setUp()

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
        self.assertEqual(len(load['results']), Comment.objects.count())

    def test_put_detail(self):
        # forbidden for non privileged user, use: patch instead
        self.login('user')
        put = deepcopy(self.put)
        # no one except privileged users can modify user field freely
        put.update({
            'user': reverse('api:user-detail', args=(self.user.pk, ))
        })
        count = Comment.objects.count()
        response = self.client.put(self.url_put, data=put,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(
            load['detail'],
            'You do not have permission to perform this action.')

    def test_post_list(self):
        self.login('user')
        count = Comment.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')

        load = json.loads(response.content)
        post = deepcopy(self.post)

        self.assertEqual(Comment.objects.count(), count + 1)
        self.check_response(load, post)

    def test_patch_detail(self):
        self.login('user')
        count = Comment.objects.count()
        response = self.client.patch(self.url_patch, data=self.patch,
                                     format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        obj = Comment.objects.get(pk=self.comment.pk)
        self.check_instance(obj, load, self.patch)
        self.assertEqual(Comment.objects.count(), count)

    def test_delete_detail(self):
        self.login('user')
        count = Comment.objects.count()
        response = self.client.delete(self.url_delete, data={},
                                      format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), count - 1)


class CommentViewSetUserNotOwnerTest(CommentViewSetTestMixin, TestHelperMixin,
                                     APITestCase):
    # test non-privileged user
    # he isn't owner of comment so there's restricted rights around
    def setUp(self):
        super(CommentViewSetUserNotOwnerTest, self).setUp()

    def test_get_detail(self):
        """Anyone except sender, addressee would retrieve 404"""
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
        self.assertEqual(len(load['results']), Comment.objects.count())

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

    def test_post_list_failure(self):
        """
        any user can create his own comment, whatever user would post
        the owner by default is bind for his/hers id

        :return:
        """
        self.login('user2')
        count = Comment.objects.count()
        response = self.client.post(self.url_post, data=self.post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(Comment.objects.count(), count)
        self.assertEqual(
            load['user'][0],
            unicode(_("You can only post comment using your user id"))
        )

    def test_post_list(self):
        """
        any user can create his own comment, whatever user would post
        the owner by default is bind for his/hers id

        :return:
        """
        self.login('user2')
        post = deepcopy(self.post)
        post.update({
            'user': reverse('api:user-detail', args=(self.other_user.pk, ))
        })
        count = Comment.objects.count()
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(Comment.objects.count(), count + 1)
        self.check_response(load, post)

    def test_post_list_no_user_set(self):
        """
        check comment creation without user field passage
        (should create comment that binding to its creator/initiator)

        :return:
        """
        self.login('user2')
        post = deepcopy(self.post)
        post.pop('user')

        count = Comment.objects.count()
        response = self.client.post(self.url_post, data=post,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response['Content-Type'], 'application/json')
        load = json.loads(response.content)
        self.assertEqual(Comment.objects.count(), count + 1)
        self.check_response(load, post)
        comment = Comment.objects.latest('pk')
        self.assertEqual(comment.user, self.other_user)

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