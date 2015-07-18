# coding: utf-8

from django.test import TestCase
from apps.accounts.models import User
from apps.tabletop.models import Codex, Roster
from apps.core.tests import TestHelperMixin
from django.core.urlresolvers import reverse

from copy import deepcopy
import allure
from allure.constants import Severity


@allure.feature('General: Rosters')
class RosterTest(TestHelperMixin, TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_games.json',
        'load_missions.json',
        'load_codexes.json',
    ]

    post = {
        'codex': 1,
        'title': u'Новый ростер',
        'roster': u'Содержимое нового ростера',
        'pts': 555,
        'revision': 4,
    }
    post_update = {
        'codex': 1,
        'title': u'Редактированный ростер',
        'roster': u'Новое содержимое',
        'pts': 1000,
        'revision': 5
    }

    def setUp(self):
        self.codex = Codex.objects.get(pk=1)
        self.user = User.objects.get(username='user')

    def add_roster(self, user=None):
        user = user or self.user
        post = deepcopy(self.post)
        post.pop('codex')

        roster = Roster.objects.create(
            owner=user, codex=self.codex, **post
        )
        return roster

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_roster_add(self):
        self.login('user')
        url = reverse('tabletop:roster-add')
        count = Roster.objects.count()
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Roster.objects.count(), count + 1)
        roster = Roster.objects.latest('pk')
        post = deepcopy(self.post)
        post.update({
            'codex': self.codex
        })
        self.check_state(roster, post, self.assertEqual)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_roster_update(self):
        roster = self.add_roster()
        self.login(user=roster.owner    .username)
        response = self.client.post(roster.get_edit_url(), self.post_update,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        post = deepcopy(self.post_update)
        post.update({
            'codex': Codex.objects.get(pk=post['codex'])
        })
        roster = Roster.objects.get(pk=roster.pk)
        self.check_state(roster, post, self.assertEqual)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_roster_update_failure(self):
        roster = self.add_roster(self.user)
        self.login('admin')
        response = self.client.post(roster.get_edit_url(), self.post_update,
                                    follow=True)
        self.assertEqual(response.status_code, 404)
        roster = Roster.objects.get(pk=roster.pk)
        post = deepcopy(self.post_update)
        post.pop('codex')
        self.check_state(roster, post, self.assertNotEqual)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_roster_delete(self):
        roster = self.add_roster()
        self.login(user=roster.owner.username)
        response = self.client.post(roster.get_delete_url(), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Roster.objects.filter(pk=roster.pk).exists(), False)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_roster_delete_failure(self):
        roster = self.add_roster()
        self.login(user='admin')
        response = self.client.post(roster.get_delete_url(), {}, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Roster.objects.filter(pk=roster.pk).exists(), True)
