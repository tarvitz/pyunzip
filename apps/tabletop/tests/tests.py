# coding: utf-8

from django.test import TestCase
from apps.tabletop.models import Codex, Roster, Report
from apps.core.tests import TestHelperMixin
from django.contrib.auth import get_user_model

from apps.wh.models import Army, Side
from apps.core.helpers import get_content_type

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.text import force_text

from django.core import exceptions
from django.conf import settings

from copy import deepcopy
import allure
from allure.constants import Severity

User = get_user_model()


@allure.feature('Roster')
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


@allure.feature('Codex')
class CodexTest(TestHelperMixin, TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
        'load_universes.json',
        'load_sides.json',
        'load_armies.json',
    ]

    def setUp(self):
        self.side = Side.objects.get(pk=1)
        self.army = Army.objects.get(pk=1)
        self.side_ct = get_content_type(self.side)
        self.army_ct = get_content_type(self.army)

        self.post_side = {
            'side': self.side.pk,
            'title': u'Vanilla',
            'revisions': '1,2,3,4,5'
        }
        self.post_army = {
            'army': self.army.pk,
            'title': u'Vanilla',
            'revisions': '1,2,3'
        }
        self.post = {
            'army': self.army.pk,
            'side': self.side.pk,
            'title': u'Army codex',
            'revisions': '1,2,3,4'
        }

    def add_codex(self):
        codex = Codex.objects.create(
            content_type=self.side_ct, object_id=self.side.pk,
            title=u'New codex', revisions='1,2,3,4,5'
        )
        return codex

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_codex_side_create(self):
        self.login('admin')
        # side bind
        count = Codex.objects.count()
        url = reverse('tabletop:codex-add')
        response = self.client.post(url, self.post_side, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Codex.objects.count(), count + 1)
        codex = Codex.objects.latest('pk')
        self.assertEqual(codex.content_type, self.side_ct)
        self.assertEqual(codex.object_id, self.side.pk)
        self.assertEqual(codex.title, self.post_side['title'])
        self.assertEqual(codex.revisions, self.post_side['revisions'])

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_codex_army_create(self):
        self.login('admin')
        # army bind
        count = Codex.objects.count()
        url = reverse('tabletop:codex-add')
        response = self.client.post(url, self.post_army, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Codex.objects.count(), count + 1)
        codex = Codex.objects.latest('pk')
        self.assertEqual(codex.content_type, self.army_ct)
        self.assertEqual(codex.object_id, self.army.pk)
        self.assertEqual(codex.title, self.post_army['title'])
        self.assertEqual(codex.revisions, self.post_army['revisions'])

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_codex_army_is_prior_create(self):
        """
        army is prior for codex bindings, so if user would pass side and army
        only army would be identified for codex binding

        :return:
        """
        self.login('admin')
        # army bind
        count = Codex.objects.count()
        url = reverse('tabletop:codex-add')
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Codex.objects.count(), count + 1)
        codex = Codex.objects.latest('pk')
        self.assertEqual(codex.content_type, self.army_ct)
        self.assertEqual(codex.object_id, self.army.pk)
        self.assertEqual(codex.title, self.post['title'])
        self.assertEqual(codex.revisions, self.post['revisions'])

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_codex_create_failure(self):
        self.login('user')
        count = Codex.objects.count()
        url = reverse('tabletop:codex-add')
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Codex.objects.count(), count)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_codex_update(self):
        codex = self.add_codex()
        self.login('admin')
        url = codex.get_edit_url()
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        codex = Codex.objects.get(pk=codex.pk)
        self.assertEqual(codex.content_type, self.army_ct)
        self.assertEqual(codex.object_id, self.army.pk)
        self.assertEqual(codex.title, self.post['title'])
        self.assertEqual(codex.revisions, self.post['revisions'])

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_codex_update_failure(self):
        codex = self.add_codex()
        self.login('user')
        url = codex.get_edit_url()
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 403)
        codex = Codex.objects.get(pk=codex.pk)
        self.assertNotEqual(codex.content_type, self.army_ct)
        self.assertNotEqual(codex.title, self.post['title'])
        self.assertNotEqual(codex.revisions, self.post['revisions'])

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_codex_delete(self):
        codex = self.add_codex()
        self.login('admin')
        count = Codex.objects.count()
        url = codex.get_delete_url()
        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Codex.objects.count(), count - 1)
        self.assertEqual(Codex.objects.filter(pk=codex.pk).exists(), False)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_codex_delete_failure(self):
        codex = self.add_codex()
        self.login('user')
        count = Codex.objects.count()
        url = codex.get_delete_url()
        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Codex.objects.count(), count)
        self.assertEqual(Codex.objects.filter(pk=codex.pk).exists(), True)


@allure.feature('Report')
class ReportTest(TestHelperMixin, TestCase):
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
        'load_armies.json',
        'load_sides.json',
        'load_codexes.json',
        'load_rosters.json',
    ]

    def setUp(self):
        side_ct = get_content_type(Side)
        Codex.objects.filter(content_type_id=17).update(content_type=side_ct)
        self.winners = Roster.objects.filter(pk__in=[1, ])
        self.rosters = Roster.objects.filter(pk__in=[1, 2])
        self.post = {
            'title': u'Report',
            'comment': u'Comment',
            'winners': [1, ],
            'rosters': [1, 2],
            'is_draw': False,
            'layout': '1vs1'
        }
        self.post_update = {
            'title': u'New report',
            'comment': u'New comments',
            'winners': [2, ],
            'rosters': [1, 2],
            'is_draw': False,
            'layout': '1vs1'
        }
        self.post_update_failure = {
            'winners': [3, 4],
            'rosters': [1, 2]
        }
        self.user = User.objects.get(username='user')
        self.admin = User.objects.get(username='admin')
        self.create_url = reverse('tabletop:report-create')

    def add_report(self, user=None):
        user = user or self.user
        report = Report.objects.create(
            owner=user,
            title=self.post['title'], comment=self.post['comment'],
            is_draw=self.post['is_draw'], layout=self.post['layout']
        )
        for winner in self.winners:
            report.winners.add(winner)
        for roster in self.rosters:
            report.rosters.add(roster)
        report.save()
        return report

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_report_anonymous_create(self):
        response = self.client.post(self.create_url, self.post, follow=True)
        self.assertEqual(response.status_code, 404)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_report_anonymous_update(self):
        report = self.add_report()
        response = self.client.post(report.get_edit_url(), self.post,
                                    follow=True)
        self.assertEqual(response.status_code, 404)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_report_anonymous_delete(self):
        report = self.add_report()
        response = self.client.post(report.get_delete_url(), {},
                                    follow=True)
        self.assertEqual(response.status_code, 404)

    @allure.story('get')
    @allure.severity(Severity.CRITICAL)
    def test_report_list(self):
        self.add_report()
        url = reverse('tabletop:report-list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('object_list', context)
        self.assertEqual(context['object_list'].count(), 1)

    @allure.story('get')
    @allure.severity(Severity.CRITICAL)
    def test_report_get(self):
        report = self.add_report()
        response = self.client.get(report.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('object', context)
        self.assertIsInstance(context['object'], Report)

    @allure.story('create')
    @allure.severity(Severity.CRITICAL)
    def test_report_user_create(self):
        self.login('user')
        count = Report.objects.count()
        response = self.client.post(self.create_url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        self.assertEqual(Report.objects.count(), count + 1)
        report = Report.objects.latest('pk')
        self.assertEqual(report.owner, self.user)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_report_user_update(self):
        report = self.add_report(user=self.user)
        self.login('user')
        response = self.client.post(report.get_edit_url(), self.post_update,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        report = Report.objects.get(pk=report.pk)
        self.assertInstance(report, self.post_update)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_report_user_delete(self):
        report = self.add_report(user=self.user)
        self.login('user')
        count = Report.objects.count()
        response = self.client.post(report.get_delete_url(), {}, follow=True)
        # check we passes through deletion link
        self.assertEqual(response.status_code, 200)
        # check we delete something from reports
        self.assertEqual(Report.objects.count(), count - 1)
        # check we delete exactly that instance we wanted to
        self.assertRaises(exceptions.ObjectDoesNotExist,
                          lambda: Report.objects.get(pk=report.pk))

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_report_user_update_non_owner(self):
        """ non-owner's can not update/delete reports of non their own """
        report = self.add_report(user=self.admin)
        self.login('user')
        response = self.client.post(report.get_edit_url(), self.post_update,
                                    follow=True)
        self.assertEqual(response.status_code, 403)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_report_user_delete_non_owner(self):
        """ non-owner's can not update/delete reports of non their own """
        report = self.add_report(user=self.admin)
        self.login('user')
        response = self.client.post(report.get_delete_url(), {},
                                    follow=True)
        self.assertEqual(response.status_code, 403)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_report_admin_update_non_owner(self):
        """ admin users can freely modify/delete reports that don't belng to
        them
        """
        report = self.add_report(user=self.user)
        self.login('admin')
        response = self.client.post(report.get_edit_url(), self.post_update,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(pk=report.pk)
        self.assertInstance(report, self.post_update)

    @allure.story('delete')
    @allure.severity(Severity.CRITICAL)
    def test_report_admin_delete_non_owner(self):
        """ admin users can delete reports that does not belong to them freely
        """
        report = self.add_report(user=self.user)
        count = Report.objects.count()
        self.login('admin')
        response = self.client.post(report.get_delete_url(), {},
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Report.objects.count(), count - 1)
        self.assertRaises(exceptions.ObjectDoesNotExist,
                          lambda: Report.objects.get(pk=report.pk))

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_report_user_update_failure(self):
        report = self.add_report(user=self.user)
        self.login('user')
        response = self.client.post(report.get_edit_url(),
                                    self.post_update_failure, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        form = response.context['form']
        self.assertNotEqual(form.errors, {})
        # winners should be represented withing selected rosters
        winners = Roster.objects.filter(
            pk__in=self.post_update_failure['winners'])
        for winner in winners:
            self.assertIn(
                force_text(
                    _("There's no such winner `%s` in rosters") % (
                        winner.__str__(), )
                ),
                form.errors['winners']
            )
