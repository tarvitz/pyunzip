# coding: utf-8

from django.test import TestCase
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from apps.wh.models import (
    Rank, RankType
)

from apps.core.tests import TestHelperMixin
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils.unittest import skipIf

from apps.core.helpers import get_object_or_None
from django.core.cache import cache


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

    def test_rank_view(self):
        rank = Rank.objects.all()[0]
        url = reverse('wh:ranks', args=(rank.id, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


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
