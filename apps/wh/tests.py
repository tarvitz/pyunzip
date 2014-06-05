# coding: utf-8
#from django.utils import unittest

import re
from django.test import TestCase
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from apps.wh.models import (
    Side, RegisterSid, Rank, RankType, PM
)
from apps.core.models import UserSID
from apps.core.tests import TestHelperMixin
from django.core.urlresolvers import reverse, reverse_lazy, NoReverseMatch
from django.utils.unittest import skipIf

from apps.core.helpers import get_object_or_None
from copy import deepcopy
from django.core.cache import cache
import simplejson as json


class ImplementMe(Exception):
    pass


class JustTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_rank_types.json',
        'tests/fixtures/load_ranks.json',
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_pms.json'
    ]

    def setUp(self):
        self.urls_void = [
        ]
        self.urls_registered = [
            reverse_lazy('wh:users'),
        ]
        self.get_object = get_object_or_None

    def test_registered_urls(self):
        messages = []
        for user in ('admin', 'user', ):
            logged = self.client.login(username=user, password='123456')
            self.assertEqual(logged, True)
            for url in self.urls_registered:
                try:
                    response = self.client.get(url, follow=True)
                    try:
                        self.assertEqual(response.status_code, 200)
                    except AssertionError as err:
                        messages.append({
                            'user': user, 'err': err, 'url': url,
                            'type': 'Assertion'
                        })
                except NoReverseMatch as err:
                    messages.append({
                        'user': user, 'err': err, 'url': url,
                        'type': 'NoReverseMatch'
                    })
        if messages:
            for msg in messages:
                print "Got %(type)s on %(url)s with %(user)s: %(err)s" % msg
            raise AssertionError

    def tearDown(self):
        pass

    def check_state(self, instance, data, check=lambda x: x):
        messages = []
        for (key, value) in data.items():
            try:
                check(getattr(instance, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key
                })
        if messages:
            for msg in messages:
                print "Got %(err)s in %(key)s" % msg
            raise AssertionError

    @skipIf(True, "disabled")
    def test_sulogin(self):
        # admin can login as other users (to watch bugs and something)
        # don't abuse this functional
        logged = self.client.login(username='admin', password='123456')
        u = User.objects.get(username='admin')
        self.assertEqual(u.is_superuser, True)
        self.assertEqual(logged, True)

        url = reverse('wh:superlogin')
        post = {
            'username': 'user'
        }
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Permission denied')
        self.assertContains(response, "data-owner='user'")
        # not admins can not use this
        self.client.login(user='user', password='123456')
        post.update({
            'username': 'lilfox'
        })
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Permission denied')

    def test_profile_get_avatar(self):
        avatar_url = reverse('wh:avatar', args=('user', ))
        response = self.client.get(avatar_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('image', response.get('Content-Type'))

    def test_race_icon(self):
        messages = []
        for side in Side.objects.all():
            url = reverse('wh:race-icon', args=(side.name, ))
            response = self.client.get(url, follow=True)
            self.assertEqual(response.status_code, 200)
            try:
                self.assertEqual(response.get('Content-Type'), 'image/png')
            except AssertionError as err:
                messages.append({'err': err})
        if messages:
            for msg in messages:
                print "Race icon failed: %(err)s" % msg
            raise AssertionError

    def test_get_armies(self):
        # TODO: refactor this functional
        url = reverse('json:wh:armies', args=(1, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')

    def test_rank_view(self):
        rank = Rank.objects.all()[0]
        url = reverse('wh:ranks', args=(rank.id, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_warning_increase_deacrease(self):
        logged = self.client.login(username='admin', password='123456')
        self.assertEqual(logged, True)
        increase_url = reverse('wh:warning-alter', args=('user', 'increase'))
        response = self.client.get(increase_url, follow=True)
        self.assertEqual(response.status_code, 200)
        u = User.objects.get(username='user')
        count = u.warning_set.filter(level=1).count()
        self.assertEqual(count, 1)
        # only admins can cast warnings
        deacrease_url = reverse('wh:warning-alter', args=('user', 'decrease'))
        response = self.client.get(deacrease_url, follow=True)
        self.assertEqual(response.status_code, 200)
        count = u.warning_set.count()
        self.assertEqual(count, 0)
        # could not alter warning for user which is not exists
        increase_url = reverse('wh:warning-alter', args=('not_existing_user', 'increase'))
        response = self.client.get(increase_url)
        self.assertEqual(response.status_code, 404)

    def test_warning_alter(self):
        logged = self.client.login(username='admin', password='123456')
        self.assertEqual(logged, True)
        url = reverse('wh:warning-alter-form', args=('user', ))
        edit = {
            'level': 5
        }
        post = {
            'nickname': 'user',
            'comment': 'just deal with it'
        }
        post.update(edit)
        response = self.client.post(url, post, follow=True)

        self.assertEqual(response.status_code, 200)
        u = User.objects.get(username='user')
        self.assertEqual(u.warning_set.filter(level=1).count(), 0)
        warning = u.warning_set.filter(level=5)
        self.assertNotEqual(len(warning), 0)
        warning = warning[0]

        messages = []
        for (key, value) in edit.items():
            try:
                self.assertEqual(getattr(warning, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key
                })
        if messages:
            for msg in messages:
                print "Got error assigning: %(key)s with %(err)s" % msg
            raise AssertionError
        comment = warning.comments.filter(comment__iexact=post['comment'])
        self.assertEqual(comment.count(), 1)
        self.assertEqual(comment[0].comment, post['comment'])

    def test_send_pm(self):
        admin = User.objects.get(username='admin')
        post = {
            'addressee': admin.pk,
            'title': 'me here',
            'content': u'Preved medved, waaaGH?'
        }
        count = PM.objects.count()
        url = reverse('wh:pm-send')
        # anonymous can not post pm
        response = self.client.post(url, post, follow=True)
        self.proceed_form_errors(response.context)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(count, PM.objects.count())

        # user can post private messages
        self.client.login(username='user', password='123456')
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count + 1, PM.objects.count())
        pm = PM.objects.order_by('-id').all()[0]
        edit = deepcopy(post)
        edit.update({'addressee': admin})
        self.check_state(pm, edit, check=self.assertEqual)


    def test_json_pm_fetch(self):
        logged = self.client.login(username='user', password='123456')
        user = User.objects.get(username='user')

        self.assertEqual(logged, True)

        # inbox
        url = reverse('json:wh:pm-view')
        pm = PM.objects.filter(addressee=user)[0]
        inbox_url = "%s?pk=%s&folder=inbox" % (url, pm.pk)
        response = self.client.get(inbox_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get("Content-Type"), 'application/json')
        js = json.loads(response.content)
        self.assertEqual(js['to'], user.nickname)
        sender = User.objects.get(nickname__iexact=js['from'])
        self.assertIn(sender.nickname, js['nickname'])

        # outbox
        pm = PM.objects.filter(sender=user)[0]
        outbox_url = "%s?pk=%s&folder=outbox" % (url, pm.pk)
        response = self.client.get(outbox_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get("Content-Type"), 'application/json')
        js = json.loads(response.content)
        self.assertEqual(js['from'], user.nickname)
        addressee = User.objects.get(nickname__iexact=js['to'])
        self.assertIn(addressee.nickname, js['nickname'])


class CacheTest(TestCase):
    fixtures = [
        'tests/fixtures/load_rank_types.json',
        'tests/fixtures/load_ranks.json',
        'tests/fixtures/load_users.json',
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def cache_delete_nickname(self, user):
        cache.delete('nick:%s' % user.username)

    def cache_get_nickname(self, user):
        return cache.get('nick:%s' % user.username)

    def test_user_change_get_nickname_test(self):
        user = User.objects.get(username='user')
        logged = self.client.login(username='user', password='123456')
        nickname = user.get_nickname(no_cache=True)
        self.assertNotEqual(nickname, '')
        self.cache_delete_nickname(user)
        self.assertEqual(logged, True)

        rank_type = RankType.objects.get(id=1)
        ranks = user.ranks.filter(pk__in=rank_type.rank_set.all())
        self.assertNotEqual(ranks.count(), 0)
        self.cache_delete_nickname(user)
        self.assertEqual(self.cache_get_nickname(user), None)
        # trying to fetch it via changing type
        rank_type = RankType.objects.get(pk=rank_type.pk)
        rank_type.save()
        self.assertEqual(self.cache_get_nickname(user), nickname)
        # trying to fetch it via user change
        self.cache_delete_nickname(user)
        user = User.objects.get(pk=user.pk)
        user.save()
        self.assertEqual(self.cache_get_nickname(user), nickname)
