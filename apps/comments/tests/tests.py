# coding: utf-8
from apps.news.models import Event
from apps.accounts.models import User
from apps.comments.models import CommentWatch, Comment
from apps.comments import utils
from apps.core.helpers import get_content_type
from apps.core.tests import TestHelperMixin
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from rest_framework.test import APITestCase

import allure
from allure.constants import Severity


# noinspection PyUnresolvedReferences
class CommentWatchBase(object):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_event_places.json',
        'load_events.json',
        'load_comments.json',
    ]

    def setUp(self):
        self.event = Event.objects.latest('pk')
        self.event_ct = get_content_type(self.event)
        self.object_pk = self.event.pk
        self.user = User.objects.get(username='user')
        self.subscriptions_url = reverse('comments:subscriptions')

        self.create_dict = {
            'content_type': self.event_ct,
            'object_pk': self.event.pk,
            'user': self.user,
            'is_updated': False,
            'is_disabled': False
        }
        self.post_comment = {
            'comment': u'Новый коммент',
            'site': 1,
            'url': None,
            'syntax': 'textile',
            'content_type': self.event_ct.pk,
            'object_pk': self.event.pk
        }
        self.post_remove_subscription = {
            'agree': True
        }
        self.post_update_subscription = {
            'is_updated': False,
        }

    def make_comment(self, role='admin', status_code=200):
        self.login(role)
        count = Comment.objects.count()
        comment_url = reverse('comments:comment-add')
        response = self.client.post(comment_url, self.post_comment,
                                    follow=True)
        self.assertEqual(response.status_code, status_code)
        if response.context:
            self.proceed_form_errors(response.context)
        self.assertEqual(Comment.objects.count(), count + 1)


@allure.feature('General: Comment Watches')
class CommentWatchTest(TestHelperMixin, CommentWatchBase, TestCase):
    """
    general CommentWatch test
    """
    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_add_subscription(self):
        """
        test add new subscription for new users' comments

        :return: None
        """
        self.login('user')
        user = User.objects.get(username='user')
        count = CommentWatch.objects.count()
        event_ct = get_content_type(self.event)
        url = reverse('comments:subscription-add',
                      args=(event_ct.pk, self.event.pk))

        sign_up = dict(agree=True, content_type=event_ct.pk,
                       object_pk=self.event.pk)

        response = self.client.post(url, sign_up, follow=True)
        self.proceed_form_errors(response.context)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(CommentWatch.objects.count(), count + 1)
        comment_watch = CommentWatch.objects.latest('pk')
        self.assertEqual(comment_watch.user, user)
        self.assertEqual(comment_watch.is_disabled, False)
        self.assertEqual(comment_watch.is_updated, False)
        self.assertEqual(comment_watch.get_new_comments().count(), 0)

    @allure.story('use')
    @allure.severity(Severity.CRITICAL)
    def test_new_comments(self):
        """
        test add new comments with user subscribed for its comments

        :return: None
        """
        # create new comment, comment watch for user
        comment_watch = CommentWatch.objects.create(**self.create_dict)
        cw_count = comment_watch.get_new_comments().count()
        self.assertEqual(cw_count, 0)

        self.make_comment('admin')

        self.login('user')
        self.assertEqual(comment_watch.get_new_comments().count(),
                         cw_count + 1)

        subscriptions_url = reverse('comments:subscriptions')
        response = self.client.get(subscriptions_url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        # user page should have as many amount on comment watch instances
        # as he subscribed
        self.assertEqual(context['object_list'].count(), 1)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_remove_subscription(self):
        """
        test remove subscription test cases

        :return: None
        """
        comment_watch = CommentWatch.objects.create(**self.create_dict)
        cw_count = comment_watch.get_new_comments().count()
        self.assertEqual(cw_count, 0)
        self.make_comment('admin')

        self.assertEqual(comment_watch.get_new_comments().count(),
                         cw_count + 1)
        self.login('user')
        remove_url = comment_watch.get_subscription_remove_url()

        response = self.client.post(remove_url, self.post_remove_subscription,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        comment_watch = CommentWatch.objects.get(pk=comment_watch.pk)

        self.assertEqual(comment_watch.get_new_comments().count(), 0)
        response = self.client.get(self.subscriptions_url, follow=True)
        self.assertEqual(response.status_code, 200)

        # nothing to show to user
        self.assertEqual(response.context['object_list'].count(), 0)


@allure.feature('API: Comment Watch')
class CommentWatchApiTest(TestHelperMixin, CommentWatchBase, APITestCase):
    """
    CommentWatch test with django rest framework api integrations
    """
    @allure.story('read')
    @allure.severity(Severity.CRITICAL)
    def test_update_subscription_read(self):
        """
        test update subscription (mark all read) with drf api

        :return: None
        """
        with allure.step('setup environment'):
            comment_watch = CommentWatch.objects.create(**self.create_dict)
            cw_count = comment_watch.get_new_comments().count()
            self.assertEqual(cw_count, 0)
            self.make_comment('admin', status_code=200)

            self.assertEqual(comment_watch.get_new_comments().count(),
                             cw_count + 1)
            self.login('user')
        with allure.step('update comment watch'):
            url = reverse('api:commentwatch-detail', args=(comment_watch.pk, ))
            response = self.client.patch(url, self.post_update_subscription,
                                         format='json',
                                         follow=True)
            self.assertEqual(response.status_code, 200)
            comment_watch = CommentWatch.objects.get(pk=comment_watch.pk)
            self.check_state(comment_watch, self.post_update_subscription,
                             self.assertEqual)
            # new comments are persist anyway but user should not get access
            # to them
            self.assertEqual(comment_watch.get_new_comments().count(),
                             cw_count + 1)
            response = self.client.get(self.subscriptions_url, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['object_list'].count(), 0)


@allure.feature('General: Comments')
class CommentRanksTest(TestHelperMixin, TestCase):
    """
    Comment ranking test

    comment rank shows comment possition according to its history/placement
    """

    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_event_places.json',
        'load_events.json',
        'load_comments.json',
    ]

    def setUp(self):
        self.event_ct = ContentType.objects.get_for_model(Event)
        self.event = Event.objects.get(pk=1)
        self.redis_client = utils.get_redis_client()

    def tearDown(self):
        self.redis_client.flushdb()

    def add_comment(self, user='admin', password='123456', **comment):
        with allure.step('setup environment'):
            self.assertTrue(
                self.client.login(username=user, password=password)
            )
            comment_default = {
                'comment': u'Новый коммент',
                'site': 1,
                'url': None,
                'syntax': 'textile',
                'content_type': self.event_ct.pk,
                'object_pk': self.event.pk
            }
            count = Comment.objects.count()
            post_comment = dict(**comment_default)
            post_comment.update(**comment)
            url = reverse('comments:comment-add')
        with allure.step('post comment'):
            response = self.client.post(url, post_comment, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertResponseStatus(response, 200)
            self.assertEqual(Comment.objects.count(), count + 1)

    @allure.story('ranks')
    @allure.severity(Severity.NORMAL)
    def test_comment_rank_store(self):
        with allure.step('setup environment'):
            self.assertTrue(self.client.login(username='user',
                                              password='123456'))
        with allure.step('add comments'):
            self.add_comment(user='admin', comment='Коммент #1')
            self.add_comment(user='user', comment='Коммент #2')
            self.add_comment(user='admin', comment='Коммент #3')
            self.add_comment(user='user', comment='Коммент #4')
            self.add_comment(user='admin', comment='Коммент #5')
        with allure.step('store ranks'):
            utils.store_comment_positions(self.event)
            with allure.step('check stored'):
                self.assertEqual(utils.get_count(self.event), 5)

    @allure.story('ranks')
    @allure.severity(Severity.NORMAL)
    def test_comment_rank_get(self):
        with allure.step('setup environment'):
            self.assertTrue(self.client.login(username='user',
                                              password='123456'))
        with allure.step('add comments'):
            self.add_comment(user='admin', comment='Коммент #1')
            self.add_comment(user='user', comment='Коммент #2')
            self.add_comment(user='admin', comment='Коммент #3')
            self.add_comment(user='user', comment='Коммент #4')
            self.add_comment(user='admin', comment='Коммент #5')
        with allure.step('store ranks'):
            utils.store_comment_positions(self.event)
            with allure.step('check stored'):
                self.assertEqual(utils.get_count(self.event), 5)
        with allure.step('get rank'):
            comment = Comment.objects.latest('pk')
            rank = utils.get_comment_position(self.event, comment.pk)
            self.assertEqual(rank, 4)
