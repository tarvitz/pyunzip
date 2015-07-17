"""Poll tests, everything related to polls

.. module:: pybb.tests.polls
    :platform: Linux, Unix, Windows
    :synopsis: Tests for forum polls
.. moduleauthor: Saul Tarvitz <tarvitz@blacklibrary.ru>
"""

# coding: utf-8
from datetime import datetime, timedelta
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.db.models import Q
from apps.core.helpers import get_object_or_None
from apps.core.tests import TestHelperMixin
from apps.pybb.models import Poll, PollItem, PollAnswer, Topic
from apps.pybb.cron import UpdatePollJob
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
import allure
from allure.constants import Severity


@allure.feature('Poll')
class PollTest(TestHelperMixin, TestCase):
    """ TestCase for polls creation, update and deletion actions and logic """
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_pybb_categories.json',
        'tests/fixtures/load_forums.json',
        'tests/fixtures/load_topics.json',
        'tests/fixtures/load_posts.json',
    ]
    poll_post = {
        'title': 'Poll',
        'items_amount': 4,
        'is_multiple': True,
        'date_expire': datetime.now() + timedelta(days=7)
    }

    def setUp(self):
        self.topic = get_object_or_None(Topic, pk=1)

    def add_poll(self, role='admin'):
        """ check if possible create Poll instance.
        This uses in some tests below

        :param role: username as role
        :return:
        """
        self.login(role)
        url = self.topic.get_poll_add_url()
        count = Poll.objects.count()

        response = self.client.post(url, self.poll_post, follow=True)
        self.assertEqual(Poll.objects.count(), count + 1)
        poll = Poll.objects.latest('id')
        context = response.context
        self.assertEqual(context['request'].get_full_path(),
                         reverse('pybb:poll-configure', args=(poll.pk, )))
        self.assertEqual(response.status_code, 200)
        formset = context['form']
        self.assertEqual(len(formset.forms), self.poll_post['items_amount'])
        self.check_state(poll, self.poll_post, self.assertEqual)
        return poll

    def add_poll_items(self, role='admin'):
        """ check if possible to create Poll items within already created
        poll instance.

        :param role: username as role
        :return:
        """
        poll = self.add_poll(role)
        poll_items_count = self.poll_post['items_amount']
        count = PollItem.objects.count()

        post = {
            'poll_item_poll_set-TOTAL_FORMS': 4,
            'poll_item_poll_set-INITIAL_FORMS': 0,
            'poll_item_poll_set-MAX_NUM_FORMS': (
                settings.MAXIMUM_POLL_ITEMS_AMOUNT
            ),
            'poll_item_poll_set-0-title': 'Variant 1',
            'poll_item_poll_set-1-title': 'Variant 2',
            'poll_item_poll_set-2-title': 'Variant 3',
            'poll_item_poll_set-3-title': 'Variant 4',
        }
        response = self.client.post(poll.get_configure_url(), post,
                                    follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(PollItem.objects.count(), count + poll_items_count)
        self.assertEqual(poll.items.count(), poll_items_count)
        return poll

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_add_poll(self, role='admin'):
        """ create poll in 2 steps """
        self.add_poll_items(role)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_update_poll(self, role='admin'):
        poll = self.add_poll_items(role)
        items_amount = poll.items.count()
        url = poll.get_update_url()
        post = {
            'title': u'new poll title',
            'items_amount': items_amount + 1
        }
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['request'].get_full_path(),
                         reverse('pybb:poll-configure', args=(poll.pk, )))

        items_post = {
            'poll_item_poll_set-TOTAL_FORMS': 5,
            'poll_item_poll_set-INITIAL_FORMS': 4,
            'poll_item_poll_set-MAX_NUM_FORMS': (
                settings.MAXIMUM_POLL_ITEMS_AMOUNT
            ),
            'poll_item_poll_set-0-title': 'Variant 1',
            'poll_item_poll_set-0-id': 1,
            'poll_item_poll_set-1-title': 'Variant 2',
            'poll_item_poll_set-1-id': 2,
            'poll_item_poll_set-2-title': 'Variant 3',
            'poll_item_poll_set-2-id': 3,
            'poll_item_poll_set-3-title': 'Variant 4',
            'poll_item_poll_set-3-id': 4,
            'poll_item_poll_set-4-title': 'Variant 5',
        }
        response = self.client.post(poll.get_configure_url(),
                                    items_post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)

        self.assertEqual(poll.items.count(), items_amount + 1)

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_add_full_clean_poll_item(self, role='admin'):
        poll = self.add_poll(role)
        post = {
            'poll_item_poll_set-TOTAL_FORMS': 4,
            'poll_item_poll_set-INITIAL_FORMS': 0,
            'poll_item_poll_set-MAX_NUM_FORMS': (
                settings.MAXIMUM_POLL_ITEMS_AMOUNT
            ),
            'poll_item_poll_set-0-title': '',
            'poll_item_poll_set-1-title': '',
            'poll_item_poll_set-2-title': '',
            'poll_item_poll_set-3-title': '',
        }
        response = self.client.post(poll.get_configure_url(), post,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertNotEqual(form.errors, {})
        for item in form.errors:
            self.assertEqual(
                item['title'][0], unicode(_("Title should be set"))
            )

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_add_poll_item_unclean(self, role='admin'):
        poll = self.add_poll(role)
        post = {
            'poll_item_poll_set-TOTAL_FORMS': 4,
            'poll_item_poll_set-INITIAL_FORMS': 0,
            'poll_item_poll_set-MAX_NUM_FORMS': (
                settings.MAXIMUM_POLL_ITEMS_AMOUNT
            ),
            'poll_item_poll_set-0-title': 'Variant 1',
            'poll_item_poll_set-1-title': 'Variant 2',
            'poll_item_poll_set-2-title': '',
            'poll_item_poll_set-3-title': 'Variant 4',
        }
        response = self.client.post(poll.get_configure_url(), post,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertNotEqual(form.errors, {})
        self.assertEqual(form.errors[2]['title'][0],
                         unicode(_("Title should be set")))


@allure.feature('Poll Answer')
class PollAnswerTest(TestHelperMixin, TestCase):
    """ TestCase for voting polls actions and logic """
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_pybb_categories.json',
        'tests/fixtures/load_forums.json',
        'tests/fixtures/load_topics.json',
        'tests/fixtures/load_posts.json',
        'tests/fixtures/load_polls.json',
        'tests/fixtures/load_poll_items.json'
    ]

    def setUp(self):
        # poll 1 is multicheck
        self.multiple_poll = Poll.objects.get(pk=1)
        self.multiple_poll.date_expire = datetime.now() + timedelta(weeks=1)
        self.multiple_poll.save()

        self.single_poll = Poll.objects.get(pk=2)
        self.single_poll.date_expire = datetime.now() + timedelta(weeks=1)
        self.single_poll.save()

    @allure.story('vote')
    @allure.severity(Severity.CRITICAL)
    def test_multiple_poll_vote(self):
        """ successful multiple poll vote action/logic """
        self.login('user')
        url = self.multiple_poll.get_vote_url()
        pks = map(lambda x: x['pk'], self.multiple_poll.items.values('pk'))

        post = {
            'vote': pks[0:2],
        }
        amount = len(post['vote'])

        count = PollAnswer.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)

        self.assertEqual(PollAnswer.objects.count(), count + amount)
        # check voted users
        self.assertEqual(len(self.multiple_poll.get_voted_users()), 1)
        user = User.objects.get(username='user')
        self.assertEqual(self.multiple_poll.get_voted_users()[0], user)

    @allure.story('vote')
    @allure.severity(Severity.CRITICAL)
    def test_single_poll_vote(self):
        """ successful single poll vote action/logic """
        self.login('user')
        url = self.single_poll.get_vote_url()
        pks = map(lambda x: x['pk'], self.single_poll.items.values('pk'))
        post = {
            'vote': pks[0]
        }
        amount = 1
        count = PollAnswer.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)

        self.assertEqual(PollAnswer.objects.count(), count + amount)
        # check voted users
        self.assertEqual(len(self.single_poll.get_voted_users()), 1)
        user = User.objects.get(username='user')
        self.assertEqual(self.single_poll.get_voted_users()[0], user)

    @allure.story('vote')
    @allure.severity(Severity.CRITICAL)
    def test_single_poll_vote_failure(self):
        """ in-successful single poll vote action/logic, user can not post
         more than one vote option"""
        self.login('user')
        url = self.single_poll.get_vote_url()
        pks = map(lambda x: x['pk'], self.single_poll.items.values('pk'))
        post = {
            'vote': pks[0:2]
        }
        amount = len(post['vote'])
        count = PollAnswer.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)

        self.assertNotEqual(PollAnswer.objects.count(), count + amount)
        # only one option is valid
        self.assertEqual(PollAnswer.objects.count(), count + 1)
        # check voted users
        self.assertEqual(len(self.single_poll.get_voted_users()), 1)
        user = User.objects.get(username='user')
        self.assertEqual(self.single_poll.get_voted_users()[0], user)

    @allure.story('vote')
    @allure.severity(Severity.CRITICAL)
    def test_poll_vote_when_finished(self):
        """ test if poll is not available to vote if it's finished """
        self.single_poll.is_finished = True
        self.single_poll.save()
        self.login('user')
        count = PollAnswer.objects.count()
        pks = map(lambda x: x['pk'], self.single_poll.items.values('pk'))
        post = {
            'vote': pks[0]
        }
        response = self.client.post(self.single_poll.get_vote_url(), post,
                                    follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(PollAnswer.objects.count(), count)
        self.single_poll.is_finished = False
        self.single_poll.save()


@allure.feature('Poll')
class PollManageTest(TestHelperMixin, TestCase):
    """ TestCase for managing polls: delete, update"""
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_pybb_categories.json',
        'tests/fixtures/load_forums.json',
        'tests/fixtures/load_topics.json',
        'tests/fixtures/load_posts.json',
        'tests/fixtures/load_polls.json',
        'tests/fixtures/load_poll_items.json'
    ]

    def setUp(self):
        self.poll = Poll.objects.get(pk=1)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_delete_poll(self):
        """ pybb.change_poll permission is required to delete any poll """
        self.login('admin')
        post = {
            'agree': True
        }
        count = Poll.objects.count()
        items_count = PollItem.objects.count()
        items_amount = self.poll.items.count()
        response = self.client.post(self.poll.get_delete_url(), post,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Poll.objects.count(), count - 1)
        self.assertEqual(PollItem.objects.count(), items_count - items_amount)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_delete_post_failure(self):
        """ only pybb.change_poll permission holders can delete polls """
        self.login(self.poll.topic.user.username)
        post = {
            'agree': True
        }
        count = Poll.objects.count()
        items_count = PollItem.objects.count()
        response = self.client.post(self.poll.get_delete_url(), post,
                                    follow=True)
        # permission denied
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Poll.objects.count(), count)
        self.assertEqual(PollItem.objects.count(), items_count)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_manage_poll_failure(self):
        """ non poll-owner user can not manage/update poll"""
        qset = ~Q(pk=self.poll.topic.user.pk) & ~Q(is_superuser=True)
        user = User.objects.filter(qset)[0]
        self.login(user.username)
        response = self.client.get(self.poll.get_update_url(), follow=True)
        self.assertEqual(response.status_code, 403)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_manage_poll_success(self):
        """ non poll-owner with change_poll permission can
        manage/update poll"""
        perm = Permission.objects.get(codename='change_poll')
        qset = ~Q(pk=self.poll.topic.user.pk) & ~Q(is_superuser=True)
        user = User.objects.filter(qset)[0]
        user.user_permissions.add(perm)
        user.save()

        self.login(user=user.username)
        response = self.client.get(self.poll.get_update_url(), follow=True)
        self.assertEqual(response.status_code, 200)

        # post actions
        user.user_permissions.remove(perm)
        user.save()

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_configure_poll_failure(self):
        """ non poll-owner user can not manage/update poll items"""
        qset = ~Q(pk=self.poll.topic.user.pk) & ~Q(is_superuser=True)
        user = User.objects.filter(qset)[0]
        self.login(user.username)
        response = self.client.get(self.poll.get_configure_url(), follow=True)
        self.assertEqual(response.status_code, 403)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_configure_poll_success(self):
        """ non poll-owner with change_poll permission can
        manage/update poll items"""
        perm = Permission.objects.get(codename='change_poll')
        qset = ~Q(pk=self.poll.topic.user.pk) & ~Q(is_superuser=True)
        user = User.objects.filter(qset)[0]
        user.user_permissions.add(perm)
        user.save()

        self.login(user=user.username)
        response = self.client.get(self.poll.get_configure_url(), follow=True)
        self.assertEqual(response.status_code, 200)

        # post actions
        user.user_permissions.remove(perm)
        user.save()


@allure.feature('Cron: Poll')
class TestCronJobs(TestHelperMixin, TestCase):
    """ TestCase for testing cron jobs """
    fixtures = [
        'load_users.json',
        'load_pybb_categories.json',
        'load_forums.json',
        'load_topics.json',
        'load_posts.json',
        'load_polls.json',
        'load_poll_items.json'
    ]

    def setUp(self):
        self.poll = Poll.objects.get(pk=1)

    @allure.story('job')
    @allure.severity(Severity.CRITICAL)
    def test_update_expire_job(self):
        self.poll.date_expire = datetime.now() - timedelta(seconds=1)
        self.poll.save()
        self.assertEqual(self.poll.is_finished, False)

        job = UpdatePollJob()
        job.do()
        poll = Poll.objects.get(pk=self.poll.pk)
        self.assertEqual(poll.is_finished, True)
