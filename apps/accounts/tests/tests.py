# coding: utf-8
#from django.utils import unittest
import os

from django.test import TestCase
from django.utils.unittest import skipIf
from django.conf import settings

from apps.accounts.models import User, PolicyWarning, PM
from apps.accounts.cron import PolicyWarningsMarkExpireCronJob
from apps.wh.models import (
    Rank, RankType)
from apps.core.models import UserSID
from apps.core.tests import TestHelperMixin
from django.core.urlresolvers import reverse, reverse_lazy, NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from apps.core.helpers import get_object_or_None
from copy import deepcopy
from django.core.cache import cache

from datetime import datetime, timedelta, date


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
            reverse_lazy('accounts:profile'),
            reverse_lazy('accounts:profile-by-nick', args=('user', )),
            reverse_lazy('accounts:users'),
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

    def test_login(self):
        login = {
            'username': 'user',
            'password': '123456'
        }
        url = reverse('accounts:login')
        response = self.client.post(url, login, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/logout/')

    def test_logout(self):
        self.client.login(username='user', password='123456')
        url = reverse('accounts:logout')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].is_authenticated(), False)
        #self.assertNotContains(response, '/logout/')

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
        #self.assertContains(response, "data-owner='user'")
        # not admins can not use this
        self.client.login(user='user', password='123456')
        post.update({
            'username': 'lilfox'
        })
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Permission denied')

    def test_password_change(self):
        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)

        url = reverse('accounts:password-change')
        new_password = '654321'
        post = {
            'password1': new_password,
            'password2': new_password,
            'old_password': '123456'
        }

        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        logged = self.client.login(username='user', password=new_password)
        self.assertEqual(logged, True)

    def test_password_recover(self):
        # user@blacklibrary.ru == user
        self.client.logout()
        init_url = reverse('accounts:password-restore-initiate')

        count = UserSID.objects.count()
        post = {
            'email': 'user@blacklibrary.ru'
        }

        response = self.client.post(init_url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        new_count = UserSID.objects.count()
        users_amount = UserSID.objects.filter(
            user__email='user@blacklibrary.ru').count()
        self.assertEqual(count + users_amount, new_count)
        sid = UserSID.objects.filter(user__email='user@blacklibrary.ru')[0]
        post_url = reverse('accounts:password-restore', args=(sid.sid, ))
        update = {
            'password': 'new_pass',
            'password2': 'new_pass'
        }

        response = self.client.post(post_url, update, follow=True)
        self.assertEqual(response.status_code, 200)
        logged = self.client.login(username=sid.user.username,
                                   password='new_pass')
        self.assertEqual(logged, True)

    def test_duplicate_nick_update(self):
        # can update self nickname for current nickname
        url = reverse('accounts:profile-update')
        post = {
            'nickname': 'user',
        }
        self.login('user')
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].nickname, post['nickname'])

    def test_duplicate_nick_failure(self):
        # can not update to follow nickname because it's busy
        url = reverse('accounts:profile-update')
        post = {
            'nickname': 'user'
        }
        self.login('admin')
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertNotEqual(response.context['form'].errors, {})
        form = response.context['form']
        self.assertEqual(
            form.errors['nickname'][0],
            unicode(_('Another user with %s nickname exists.' %
                      post['nickname']))
        )

    def test_profile_update(self):
        #avatar_name = 'avatar.jpg'
        avatar = open('tests/fixtures/avatar.jpg')
        edit_post = {
            'first_name': 'edited',
            'last_name': 'editor',
            'gender': 'm',  # (f)emale, (n)ot identified
            'nickname': 'real_tester',
            'jid': 'tester@jabber.org',
            #'uin': 123412,
            'about': 'Duty is our salvation',
            #'tz': 3.0
        }
        post = {
            #'skin': 1,
            #'side': 1,
            #'army': 1,
            'avatar': avatar,
        }
        post.update(edit_post)

        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)
        url = reverse('accounts:profile-update')
        response = self.client.post(url, post, follow=True)
        context = response.context
        if 'form' in context:
            form = context['form']
            if form.errors:
                print "Got form errors within posting form, proceeding:"
                for (key, error_list) in form.errors.items():
                    print "in '%s': '%s'" % (key, "; ".join(error_list))

        self.assertEqual(response.status_code, 200)
        messages = []

        user = User.objects.get(username='user')
        for (key, value) in edit_post.items():
            try:
                self.assertEqual(getattr(user, key), value)
            except AssertionError as err:
                messages.append({'err': err})
        if messages:
            for msg in messages:
                print "Can not edit user got: %(err)s" % msg
            raise AssertionError

        #self.assertEqual(user.skin.id, post['skin'])
        #self.assertEqual(user.army.id, post['army'])
        #self.assertEqual(
        #    'avatars/%s/%s' % (user.pk, avatar_name),
        #    user.avatar.name
        #)
        self.assertEqual(os.path.exists(user.avatar.path), True)
        os.unlink(user.avatar.path)

    def test_register(self):
        os.environ['RECAPTCHA_TESTING'] = 'True'
        usernames = (
            ('test_user', 'test@blacklibrary.ru', 'test_nickname'),
            ('test_user_2', 'test2@blacklibrary.ru', 'test_nickname_2')
        )
        for usern in usernames:
            post = {
                'username':  usern[0],  # 'test_user',
                'email': usern[1],      # 'test@blacklibrary.ru',
                'nickname': usern[2],   # 'test_nickname',
                'password': '123456',
                'password_repeat': '123456',
                'recaptcha_response_field': 'PASSED'
            }
            url = reverse('accounts:register')
            initial = self.client.get(url, follow=True)

            self.assertEqual(initial.status_code, 200)
            response = self.client.post(url, post, follow=True)
            self.proceed_form_errors(response.context)

            self.assertEqual(response.status_code, 200)
            logged = self.client.login(username=usern[0], password='123456')
            self.assertEqual(logged, True)

            # check login post
            login_url = reverse('accounts:login')
            login = {
                'username': usern[0],
                'password': '123456'
            }
            response = self.client.post(login_url, login, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '/logout/')

            user = User.objects.get(username=usern[0])
            edit = deepcopy(post)
            fields = ['recaptcha_response_field', 'password',
                      'password_repeat']
            for f in fields:
                del edit[f]
            self.check_state(user, edit, check=self.assertEqual)
            self.assertEqual(user.army, None)
            self.client.logout()

    def test_rank_view(self):
        rank = Rank.objects.all()[0]
        url = reverse('wh:ranks', args=(rank.id, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


    def test_banned_user(self):
        u = User.objects.get(username='user')
        u.is_active = False
        u.save()
        logged = self.client.login(username=u.username, password='123456')
        self.assertEqual(logged, False)
        response = self.client.get(reverse('pybb:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user.is_authenticated(),
                         False)

    def test_banned_user_while_session(self):
        u = User.objects.get(username='user')
        u.is_active = True
        u.save()
        logged = self.client.login(username=u.username, password='123456')
        self.assertEqual(logged, True)

        url = reverse('pybb:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user.is_authenticated(),
                         True)
        u.is_active = False
        u.save()

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].user.is_authenticated(),
                         False)


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

    @skipIf(True, "disabled")
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


class PolicyWarningTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
    ]

    def setUp(self):
        self.policy_warning = None
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')

        self.create_url = reverse('accounts:warning-create',
                                  args=(self.user.pk, ))
        self.update_url = reverse('accounts:warning-update',
                                  args=(self.user.pk, ))
        self.delete_url = reverse('accounts:warning-delete',
                                  args=(self.user.pk, ))

        self.date_expired = datetime.now() + timedelta(weeks=1)
        self.policy_warning_comment = u'Просто потому что'

        self.post = {
            'user': self.user.pk,
            'comment': self.policy_warning_comment,
            'date_expired': self.date_expired.strftime('%Y-%m-%d'),
            'is_expired': False,
            'level': 1,
        }
        self.post_update = {
            'user': self.user.pk,
            'comment': u'Новый комментарий',
            'date_expired': (
                self.date_expired + timedelta(days=2)).strftime('%Y-%m-%d'),
            'is_expired': False,
            'level': settings.READONLY_LEVEL
        }
        self.post_pm = {
            'addressee': self.admin.pk,
            'title': u'Заголовок сообщения',
            'content': u'Текст письма'
        }

    def add_policy_warning(self):
        self.policy_warning = PolicyWarning.objects.create(
            user=self.user, date_expired=self.date_expired,
            is_expired=False, comment=self.policy_warning_comment,
        )

    # CRUD tests
    def test_policy_warning_create(self, role='admin'):
        self.login(role)
        count = PolicyWarning.objects.count()
        response = self.client.post(self.create_url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)

        self.assertEqual(PolicyWarning.objects.count(), count + 1)
        policy_warning = PolicyWarning.objects.latest('pk')
        post = deepcopy(self.post)
        date_expired = date(*[int(i) for i in
                              self.post['date_expired'].split('-')])
        post.update({
            'user': self.user,
            'date_expired': date_expired
        })
        self.check_state(policy_warning, post, self.assertEqual)

    def test_policy_warning_create_failure(self, role='user'):
        self.login(role)
        count = PolicyWarning.objects.count()
        response = self.client.get(self.create_url, follow=True)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(self.create_url, self.post, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(PolicyWarning.objects.count(), count)

    def test_policy_warning_update(self, role='admin'):
        self.add_policy_warning()
        self.assertNotEqual(PolicyWarning.objects.count(), 0)
        self.login(role)
        response = self.client.post(self.policy_warning.get_edit_url(),
                                    self.post_update, follow=True)
        self.proceed_form_errors(response.context)

        self.assertEqual(response.status_code, 200)
        policy_warning = PolicyWarning.objects.get(pk=self.policy_warning.pk)
        post = deepcopy(self.post_update)
        date_expired = self.post_update['date_expired']
        date_expired = date(*[int(i) for i in date_expired.split('-')])

        post.update({
            'user': self.user,
            'date_expired': date_expired
        })
        self.check_state(policy_warning, post, self.assertEqual)

    def test_policy_warning_update_failure(self, role='user'):
        self.add_policy_warning()
        self.assertNotEqual(PolicyWarning.objects.count(), 0)
        self.login(role)
        response = self.client.get(self.policy_warning.get_edit_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(self.policy_warning.get_edit_url(),
                                    self.post_update, follow=True)
        self.assertEqual(response.status_code, 403)

    def test_policy_warning_delete(self, role='admin'):
        self.add_policy_warning()
        self.assertNotEqual(PolicyWarning.objects.count(), 0)
        self.login(role)
        count = PolicyWarning.objects.count()

        response = self.client.post(
            self.policy_warning.get_delete_url(), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PolicyWarning.objects.count(), count - 1)

    def test_policy_warning_delete_failure(self, role='user'):
        self.add_policy_warning()
        self.assertNotEqual(PolicyWarning.objects.count(), 0)
        self.login(role)
        response = self.client.get(self.policy_warning.get_delete_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(self.policy_warning.get_delete_url(),
                                    self.post_update, follow=True)
        self.assertEqual(response.status_code, 403)

    # test read only, cron and other stuff
    def test_policy_warning_cron_task_expire(self):
        self.add_policy_warning()
        self.assertEqual(self.policy_warning.is_expired, False)
        self.policy_warning.date_expired = datetime.now() - timedelta(hours=24)
        self.policy_warning.save()
        job = PolicyWarningsMarkExpireCronJob()
        job.do()
        policy_warning = PolicyWarning.objects.get(pk=self.policy_warning.pk)
        self.assertEqual(policy_warning.is_expired, True)

    def test_post_with_read_only_policy_warning(self):
        self.add_policy_warning()
        self.policy_warning.level = settings.READONLY_LEVEL
        self.policy_warning.save()

        count = PM.objects.count()
        self.login(self.user.username)  # user
        self.assertEqual(
            self.user.get_active_read_only_policy_warnings().count(), 1)

        response = self.client.post(reverse('accounts:pm-create'),
                                    self.post_pm, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].get_full_path(),
                         reverse('accounts:read-only'))
        self.assertEqual(PM.objects.count(), count)

    def test_manual_check_policy_warning_expire(self):
        self.add_policy_warning()
        self.policy_warning.level = settings.READONLY_LEVEL
        self.policy_warning.save()

        self.login('admin')
        post = deepcopy(self.post_update)
        post.update({
            'is_expired': True
        })
        response = self.client.post(self.policy_warning.get_edit_url(),
                                    post, follow=True)
        self.assertEqual(response.status_code, 200)
        policy_warning = PolicyWarning.objects.get(pk=self.policy_warning.pk)
        self.assertEqual(policy_warning.is_expired, True)
        self.assertEqual(
            self.user.get_active_read_only_policy_warnings().count(), 0)

        self.login('user')
        count = PM.objects.count()
        response = self.client.post(reverse('accounts:pm-create'),
                                    self.post_pm, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PM.objects.count(), count + 1)

    @skipIf(True, "Not implemented")
    def test_policy_warning_immunity(self):
        pass