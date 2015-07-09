# coding: utf-8
import os
import six
import logging

from django.test import TestCase
from django.conf import settings

from apps.accounts.models import User, PolicyWarning, PM
from apps.accounts.cron import PolicyWarningsMarkExpireCronJob
from apps.wh.models import Rank
from apps.core.models import UserSID
from apps.core.tests import TestHelperMixin
from django.core.urlresolvers import reverse, reverse_lazy, NoReverseMatch
from django.utils.translation import ugettext_lazy as _
from apps.core.helpers import get_object_or_None
from copy import deepcopy

from datetime import datetime, timedelta, date
import allure
from allure.constants import Severity


@allure.feature('Accounts')
class AccountTest(TestHelperMixin, TestCase):
    """
    account app general test cases
    """
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_pms.json'
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

    @allure.story('urls')
    @allure.severity(Severity.NORMAL)
    def test_registered_urls(self):
        """
        check urls related to accounts
        """
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
                logging.warning(
                    "Got %(type)s on %(url)s with %(user)s: %(err)s" % msg
                )
            raise AssertionError

    def tearDown(self):
        pass

    @allure.story('login')
    @allure.severity(Severity.BLOCKER)
    def test_login(self):
        """
        common login
        """
        login = {
            'username': 'user',
            'password': '123456'
        }
        url = reverse('accounts:login')
        response = self.client.post(url, login, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].is_authenticated(), True)
        self.assertContains(response, '/logout/')

    @allure.story('login')
    @allure.severity(Severity.CRITICAL)
    def test_login_email(self):
        """
        login with email
        """
        login = {
            'username': 'user@blacklibrary.ru',
            'password': '123456'
        }
        url = reverse('accounts:login')
        response = self.client.post(url, login, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].is_authenticated(), True)

    @allure.story('login')
    @allure.severity(Severity.CRITICAL)
    def test_login_email_failure(self):
        url = reverse('accounts:login')
        with allure.step('check with wrong password'):
            login = {
                'username': 'user@blacklibrary.ru',
                'password': 'wrongpassword'
            }
            response = self.client.post(url, login, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['user'].is_authenticated(),
                             False)
        with allure.step('check with non-existent user'):
            login = {
                'username': 'non_existentuser@example.org',
                'password': '123456'
            }
            response = self.client.post(url, login, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['user'].is_authenticated(),
                             False)

    @allure.story('logout')
    @allure.severity(Severity.NORMAL)
    def test_logout(self):
        """
        logout
        """
        self.client.login(username='user', password='123456')
        url = reverse('accounts:logout')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].is_authenticated(), False)

    @allure.story('password')
    @allure.severity(Severity.BLOCKER)
    def test_password_change(self):
        """
        password change
        """
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

    @allure.story("password")
    @allure.severity(Severity.BLOCKER)
    def test_password_recover(self):
        """
        password recover
        """
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

    @allure.story('register')
    @allure.severity(Severity.BLOCKER)
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

    @allure.story('register')
    @allure.severity(Severity.CRITICAL)
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
            six.text_type(
                _('Another user with %s nickname exists.' % post['nickname']))
        )

    @allure.story('profile')
    @allure.severity(Severity.CRITICAL)
    def test_profile_update(self):
        avatar = open('tests/fixtures/avatar.jpg')
        edit_post = {
            'first_name': 'edited',
            'last_name': 'editor',
            'gender': 'm',  # (f)emale, (n)ot identified
            'nickname': 'real_tester',
            'jid': 'tester@jabber.org',
            'about': 'Duty is our salvation',
        }
        post = {
            'avatar': avatar,
        }
        post.update(**edit_post)

        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)
        url = reverse('accounts:profile-update')
        response = self.client.post(url, post, follow=True)
        context = response.context
        if 'form' in context:
            form = context['form']
            if form.errors:
                logging.warning(
                    "Got form errors within posting form, proceeding:"
                )
                for (key, error_list) in form.errors.items():
                    logging.warning(
                        "in '%s': '%s'" % (key, "; ".join(error_list))
                    )

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
                logging.warning("Can not edit user got: %(err)s" % msg)
            raise AssertionError

        self.assertEqual(os.path.exists(user.avatar.path), True)
        os.unlink(user.avatar.path)

    @allure.story('register')
    @allure.severity(Severity.BLOCKER)
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
                'recaptcha_response_field': 'PASSED',
                'g-recaptcha-response': 'PASSED'
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
            edit = dict(**post)
            fields = ['recaptcha_response_field', 'password',
                      'password_repeat', 'g-recaptcha-response']
            for f in fields:
                del edit[f]
            self.check_state(user, edit, check=self.assertEqual)
            self.assertEqual(user.army, None)
            self.client.logout()

    @allure.story('deprecated')
    @allure.severity(Severity.NORMAL)
    def test_rank_view(self):
        rank = Rank.objects.all()[0]
        url = reverse('wh:ranks', args=(rank.id, ))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

    @allure.story('access')
    @allure.severity(Severity.NORMAL)
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

    @allure.story('access')
    @allure.severity(Severity.NORMAL)
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


@allure.feature('Policy Warnings')
class PolicyWarningTest(TestHelperMixin, TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_users.json',
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
    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_policy_warning_create(self, role='admin'):
        """
        create policy warning
        :param str role: using role (admin, user)
        """
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

    @allure.story('create')
    @allure.severity(Severity.NORMAL)
    def test_policy_warning_create_failure(self, role='user'):
        """
        create policy warning (permission denied)
        :param str role: using role (admin, user)
        """
        self.login(role)
        count = PolicyWarning.objects.count()
        response = self.client.get(self.create_url, follow=True)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(self.create_url, self.post, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(PolicyWarning.objects.count(), count)

    @allure.story('update')
    @allure.severity(Severity.NORMAL)
    def test_policy_warning_update(self, role='admin'):
        """
        update policy warning
        :param str role: using role (admin, user)
        """
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

    @allure.story('update')
    @allure.severity(Severity.NORMAL)
    def test_policy_warning_update_failure(self, role='user'):
        """
        update policy warning (permission denied)
        :param str role: using role (admin, user)
        """
        self.add_policy_warning()
        self.assertNotEqual(PolicyWarning.objects.count(), 0)
        self.login(role)
        response = self.client.get(self.policy_warning.get_edit_url(),
                                   follow=True)
        self.assertEqual(response.status_code, 403)
        response = self.client.post(self.policy_warning.get_edit_url(),
                                    self.post_update, follow=True)
        self.assertEqual(response.status_code, 403)

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_policy_warning_delete(self, role='admin'):
        """
        delete policy warning
        :param str role: using role (admin, user)
        """
        self.add_policy_warning()
        self.assertNotEqual(PolicyWarning.objects.count(), 0)
        self.login(role)
        count = PolicyWarning.objects.count()

        response = self.client.post(
            self.policy_warning.get_delete_url(), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(PolicyWarning.objects.count(), count - 1)

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_policy_warning_delete_failure(self, role='user'):
        """
        create policy warning (permission denied)
        :param str role: using role (admin, user)
        """
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
    @allure.story('cron')
    @allure.severity(Severity.NORMAL)
    def test_policy_warning_cron_task_expire(self):
        """
        policy warning cron expire test
        """
        self.add_policy_warning()
        self.assertEqual(self.policy_warning.is_expired, False)
        self.policy_warning.date_expired = datetime.now() - timedelta(hours=24)
        self.policy_warning.save()
        job = PolicyWarningsMarkExpireCronJob()
        job.do()
        policy_warning = PolicyWarning.objects.get(pk=self.policy_warning.pk)
        self.assertEqual(policy_warning.is_expired, True)

    @allure.story('read')
    @allure.severity(Severity.NORMAL)
    def test_post_with_read_only_policy_warning(self):
        """
        test post data with ``read only`` policy warning
        """
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

    @allure.story('expire')
    @allure.severity(Severity.NORMAL)
    def test_manual_check_policy_warning_expire(self):
        """
        manual check policy warning expire check
        """
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
