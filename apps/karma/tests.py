# coding: utf-8
#from django.utils import unittest
import os
from django.test import TestCase
from apps.karma.models import KarmaStatus
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from apps.core.helpers import model_json_encoder
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import simplejson as json

from apps.core.helpers import get_object_or_None


class JustTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
        'tests/fixtures/load_news.json',
        #'tests/fixtures/load_comments.json',
        'tests/fixtures/load_karma_statuses.json',
        'tests/fixtures/load_karma.json'
    ]

    def setUp(self):
        self.request_factory = RequestFactory()
        self.urls_void = [
        ]
        self.urls_registered = [
        ]
        self.urls_params = [
        ]
        self.unlink_files = []

    def tearDown(self):
        pass

    def test_get_karma_status(self):
        ks = KarmaStatus.objects.all()[0]
        url = reverse('karma:status', args=(ks.codename, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'status_%s' % ks.id)

    def test_alter_karma(self):
        # anonymous can not alter karma
        u = User.objects.get(username='user')
        admin = User.objects.get(username='admin')
        # checking anonymous
        post = {
            'comment': 'up',
            'alter': 'up',
            'url': '/news/',
            'user': u.id,
        }
        karma = u.karma
        url = reverse('karma:alter', args=('up', 'user'))
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        u = User.objects.get(id=u.id)
        self.assertEqual(u.karma, karma)

        # user applies ok
        logged = self.client.login(username='admin', password='123456')
        self.assertEqual(logged, True)
        response = self.client.post(url, post, follow=True)
        # FIXME: fix decorator returns right url, not 404
        self.assertIn(response.status_code, (200, 404))

        u = User.objects.get(id=u.id)
        self.assertEqual(karma, u.karma) # not enough power
        ct = ContentType.objects.get(
            app_label=u._meta.app_label,
            model=u._meta.module_name
        )

        admin = User.objects.get(username='admin')
        for i in range(settings.KARMA_COMMENTS_COUNT + 5):
            comment = Comment.objects.create(
                content_type=ct, object_pk=str(u.id),
                user=admin,
                comment='void', site_id=1
            )
            self.assertNotEqual(comment.id, None)

        # check can not alter karma for yourself
        logged = self.client.login(username='admin', password='123456')
        url = reverse('karma:alter', args=('up', 'admin'))
        self.assertEqual(logged, True)
        post = {
            'user': admin.id,
            'alter': 'up',
            'url': '/news/',
            'comment': 'up'
        }
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, unicode(_("You can not alter karma for yourself")))
        # check for another user
        post.update({
            'user': u.id
        })
        response = self.client.post(url, post, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.request.get('PATH_INFO'), post['url'])
        u = User.objects.get(id=u.id)
        self.assertEqual(karma + 1, u.karma)
