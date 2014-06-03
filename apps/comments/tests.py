# coding: utf-8
from apps.news.models import Event
from apps.accounts.models import User
from apps.comments.models import CommentWatch
from apps.core.helpers import get_content_type
from apps.core.tests import TestHelperMixin
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.comments.models import Comment

from rest_framework.test import APITestCase
# Create your tests here.


# noinspection PyUnresolvedReferences
class CommentWatchBase(object):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_event_places.json',
        'tests/fixtures/load_events.json',
        'tests/fixtures/load_comments.json',
    ]

    # noinspection PyAttributeOutsideInit,PyPep8Naming
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


class CommentWatchTest(TestHelperMixin, CommentWatchBase, TestCase):
    """
    general CommentWatch test
    """
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


class CommentWatchApiTest(TestHelperMixin, CommentWatchBase, APITestCase):
    """
    CommentWatch test with django rest framework api integrations
    """
    def test_update_subscription_read(self):
        """
        test update subscription (mark all read) with drf api

        :return: None
        """
        comment_watch = CommentWatch.objects.create(**self.create_dict)
        cw_count = comment_watch.get_new_comments().count()
        self.assertEqual(cw_count, 0)
        self.make_comment('admin', status_code=302)

        self.assertEqual(comment_watch.get_new_comments().count(),
                         cw_count + 1)
        self.login('user')
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