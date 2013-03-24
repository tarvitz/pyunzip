# coding: utf-8
#from django.utils import unittest
import os
from django.test import TestCase
from django.contrib.auth.models import User
#from django.test.client import RequestFactory, Client
from django.core.urlresolvers import reverse
from django.conf import settings
from apps.core.helpers import get_object_or_None


class JustTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
    ]

    def setUp(self):
        self.urls_void = [
        ]
        self.urls_registered = [
            reverse('wh:profile'),
            reverse('wh:profile-real', args=('user', )),
            reverse('wh:profile-by-nick', args=('user', )),
            reverse('wh:users'),
            reverse('wh:url_x_get_users_list_null'),
            reverse('wh:url_x_get_users_list', args=('use', )),
            reverse('wh:pm-view'),
            reverse('wh:pm-sent'),
            reverse('wh:pm-income'),
        ]
        self.get_object = get_object_or_None

    def test_registered_urls(self):
        messages = []
        for user in ('admin', 'user'):
            logged = self.client.login(username=user, password='123456')
            self.assertEqual(logged, True)
            for url in self.urls_registered:
                response = self.client.get(url, follow=True)
                try:
                    self.assertEqual(response.status_code, 200)
                except AssertionError as err:
                    messages.append({
                        'user': user, 'err': err, 'url': url
                    })
        if messages:
            for msg in messages:
                print "Got assertion on %(url)s with %(user)s: %(err)s" % msg
            raise AssertionError

    def tearDown(self):
        pass

    def test_login(self):
        login = {
            'username': 'user',
            'password': '123456'
        }
        url = reverse('wh:login')
        response = self.client.post(url, login, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/logout/')

    def test_logout(self):
        self.client.login(username='user', password='123456')
        url = reverse('wh:logout')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '/logout/')

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

    def test_password_change(self):
        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)

        url = reverse('wh:password-change')
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
        pass

    def test_profile_update(self):
        avatar_name = 'avatar.jpg'
        avatar = open('tests/fixtures/avatar.jpg')
        edit = {
            'first_name': 'edited',
            'last_name': 'editor',
            'gender': 'm',  # (f)emale, (n)ot identified
            'nickname': 'real_tester',
            'jid': 'tester@jabber.org',
            'uin': 123412,
            'about': 'Duty is our salvation',
            'tz': 3.0
        }
        post = {
            'skin': 1,
            'side': 1,
            'army': 1,
            'avatar': avatar,
        }
        post.update(edit)

        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)
        url = reverse('wh:profile-update')
        response = self.client.post(url, post, follow=True)

        self.assertEqual(response.status_code, 200)
        messages = []

        user = User.objects.get(username='user')
        for (key, value) in edit.items():
            try:
                self.assertEqual(getattr(user, key), value)
            except AssertionError as err:
                messages.append({'err': err})
        if messages:
            for msg in messages:
                print "Can not edit user got: %(err)s" % msg
            raise AssertionError

        self.assertEqual(user.skin.id, post['skin'])
        self.assertEqual(user.army.id, post['army'])
        self.assertEqual(
            'avatars/%s/%s' % (user.pk, avatar_name),
            user.avatar.name
        )
        os.lstat(user.avatar.path)

    def test_profile_get_avatar_and_photo(self):
        avatar_url = reverse('wh:avatar', args=('user', ))
        photo_url = reverse('wh:photo', args=('user', ))
        response = self.client.get(avatar_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('image', response.get('Content-Type'))
        response = self.client.get(photo_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('image', response.get('Content-Type'))

    def test_race_icon(self):
        pass

    def test_user_side_icon(self):
        pass

    def test_get_armies_raw(self):
        # TODO: refactor this functional
        url = reverse('wh:armies-raw', args=(1, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')

    def test_get_skins_raw(self):
        # TODO: refactor this functional
        url = reverse('wh:skins-raw', args=(1, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')

    def test_pm_send(self):
        pass

    def test_pm_delete(self):
        pass

    def test_register(self):
        pass

    def test_rank_view(self):
        pass

    def test_rank_edit(self):
        pass

    def test_warning_alter(self):
        pass

    def test_warning_increase_decrease(self):
        pass

    def test_miniquote_get_raw(self):
        url = reverse('wh:miniquote-get-raw')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')

    def test_favicon(self):
        url = reverse('wh:favicon')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'image/vnd.microsoft.icon')