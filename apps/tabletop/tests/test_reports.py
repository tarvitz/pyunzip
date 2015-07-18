# -*- coding: utf-8 -*-
"""
.. module:: apps.tabletop.tests.test_reports
    :synopsis: Reports test cases
.. moduleauthor:: NickolasFox <tarvitz@blacklibrary.ru>
.. sectionauthor:: NickolasFox <tarvitz@blacklibrary.ru>
"""

from django.test import TestCase
from apps.accounts.models import User
from apps.tabletop.models import Codex, Roster, Report
from apps.core.tests import TestHelperMixin

from apps.wh.models import Side
from apps.core.helpers import get_content_type

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.text import force_text

from django.core import exceptions

import allure
from allure.constants import Severity


@allure.feature('General: Reports')
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
