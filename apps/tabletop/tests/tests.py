# coding: utf-8

from django.test import TestCase
from apps.tabletop.models import Codex, Roster, Mission, Report
from apps.core.tests import TestHelperMixin
from apps.core.helpers import get_object_or_404
from django.contrib.auth import get_user_model
User = get_user_model()

from apps.wh.models import Army, Side
from apps.core.helpers import get_content_type
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.core import exceptions
from django.conf import settings
from django.core.cache import cache

from django.utils.unittest import skipIf

from copy import deepcopy


class JustTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_games.json',
        'tests/fixtures/load_missions.json',
        'tests/fixtures/load_codexes.json',
        'tests/fixtures/load_rosters.json',
        'tests/fixtures/load_battle_reports.json'
    ]

    def setUp(self):
        self.request_factory = RequestFactory()
        self.urls_void = [
            reverse('tabletop:roster', args=(1, )),
            reverse('tabletop:roster', args=(2, )),
            reverse('tabletop:roster', args=(3, )),
            reverse('tabletop:rosters-index')
        ]
        self.urls_registered = [
            reverse('tabletop:report', args=(1, )),
            reverse('tabletop:rosters'),
        ]
        self.urls_params = [
        ]
        self.unlink_files = []

    def tearDown(self):
        pass

    def check_changes(self, instance, keywords, check, check_in=None):
        messages = []
        check_in = check_in or self.assertIn
        for (key, value) in keywords.items():
            try:
                if isinstance(value, list):
                    for item in value:
                        check_in(item, getattr(instance, key).all())
                else:
                    check(getattr(instance, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key
                })
        if messages:
            for msg in messages:
                msg = "Got %(err)s in %(key)s" % msg
                print msg
            raise AssertionError

    #@skipIf(True, 'broken')
    def test_urls(self):
        # test void urls
        for user in ('user', 'admin', None):
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            else:
                self.client.logout()
            messages = []
            for url in self.urls_void:
                response = self.client.get(url, follow=True)
                try:
                    self.assertEqual(response.status_code, 200)
                except AssertionError as err:
                    messages.append({
                        'err': err,
                        'url': url
                    })
            if messages:
                for msg in messages:
                    print u"Got %(err)s in %(url)s" % msg
                raise AssertionError

    def test_roster_add(self):
        # anonymous can not upload roster
        url = reverse('tabletop:roster-add')
        codex = Codex.objects.all()[0]

        post = {
            'roster': 'roster input data',
            'pts': 555,
            'title': u'Тесты, ростер',
            'codex': codex.id,
            'revision': codex.revisions.split(',')[-1]  # last revision
        }

        count = Roster.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(count, Roster.objects.count())

        # user and admin can post normally
        for user in ('user', 'admin'):
            logged = self.client.login(username=user, password='123456')
            count = Roster.objects.count()
            self.assertEqual(logged, True)
            response = self.client.post(url, post, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(count + 1, Roster.objects.count())

    def test_battle_report_add(self):
        # anonymous can not post br
        url = reverse('tabletop:report-add')
        roster1, roster2 = list(Roster.objects.filter(pts=1000)[:2])
        mission = Mission.objects.all()[0]
        post = {
            'title': u'Батл репорт',
            'mission': mission.id,
            'rosters': [roster1.id, roster2.id],
            'winners': [roster1.id],
            'layout': '1vs1',
            'deployment': 'dow',
            'comment': u'Первый ростер победил :D'
        }
        count = Report.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(count, Report.objects.count())

        # testing for user
        logged = self.client.login(username='user', password='123456')
        user = User.objects.get(username='user')
        self.assertEqual(logged, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        open('file.html', 'w').write(response.content)
        self.assertEqual(count + 1, Report.objects.count())
        report = Report.objects.all()[0]
        edit = deepcopy(post)
        edit.update({
            'mission': mission,
            'rosters': [roster1, roster2],
            'winners': [roster1],
            'owner': user
        })

        messages = []

        for (key, value) in edit.items():
            try:
                if isinstance(value, list):
                    for item in value:
                        self.assertIn(item, getattr(report, key).all())
                else:
                    self.assertEqual(getattr(report, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key
                })
        if messages:
            for msg in messages:
                print "Got %(err)s in %(key)s" % msg
            raise AssertionError

    #@skipIf(True, "broken")
    def test_battle_report_edit(self):
        self.test_battle_report_add()
        report = Report.objects.all()[0]
        admin = User.objects.get(username='admin')
        report.owner = admin
        report.save()

        url = reverse('tabletop:report-edit', args=(report.id, ))
        roster1, roster2 = list(Roster.objects.filter(pts=1000)[:2])
        mission = Mission.objects.all()[0]
        post = {
            'title': u'Батл репорт редактирование',
            'comment': u'Первый ростер победил :D подредактирован',
            'mission': mission.id,
            'rosters': [roster1.id, roster2.id],
            'winners': [roster2.id],
            'layout': '1vs1',
            'deployment': 'ha'
        }
        edit = deepcopy(post)
        delete = ['layout', 'mission', 'rosters', 'winners',]
        for d in delete:
            del edit[d]

        for user in ('user', None):
            if user:
                self.client.login(username=user, password='123456')
            else:
                self.client.logout()
            response = self.client.post(url, post, follow=True)
            if user:
                self.assertEqual(response.status_code, 404)
            else:  # anonymous got redirect for login
                self.assertEqual(response.status_code, 404)
            report = Report.objects.get(id=report.id)
            self.check_changes(report, edit, check=self.assertNotEqual)

        edit.update({
            'rosters': [roster1, roster2],
            'winners': [roster2]
        })
        self.client.login(username='admin', password='123456')
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(id=report.id)
        self.check_changes(report, edit, check=self.assertEqual)

    #@skipIf(True, "broken")
    def test_battle_report_approve_disapprove(self):
        # only admin can approve/disapprove
        self.test_battle_report_add()
        report = Report.objects.all()[0]
        approve_url = reverse('tabletop:report-approve', args=(report.id,))
        disapprove_url = reverse('tabletop:report-disapprove', args=(report.id, ))
        for user in ('user', None):
            if user:
                self.client.login(username=user, password='123456')
            else:
                self.client.logout()
            report.approved = False
            report.save()
            response = self.client.get(approve_url, follow=True)
            if user:
                self.assertEqual(response.status_code, 404)
            else:
                self.assertEqual(response.status_code, 404)
            report = Report.objects.get(id=report.id)
            self.assertEqual(report.approved, False)
            response = self.client.get(disapprove_url, follow=True)
            if user:
                self.assertEqual(response.status_code, 404)
            else:
                self.assertEqual(response.status_code, 404)
            report = Report.objects.get(id=report.id)
            self.assertEqual(report.approved, False)
        # admin can approve
        self.client.login(username='admin', password='123456')
        report.approved = False
        report.save()
        response = self.client.get(approve_url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(id=report.id)
        self.assertEqual(report.approved, True)
        response = self.client.get(disapprove_url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = Report.objects.get(id=report.id)
        self.assertEqual(report.approved, False)

    def test_battle_report_clean_winners(self):
        logged = self.client.login(username='admin', password='123456')
        self.assertEqual(logged, True)

        url = reverse('tabletop:report-add')
        roster1, roster2 = list(Roster.objects.filter(pts=1000)[:2])
        mission = Mission.objects.all()[0]
        post = {
            'title': u'Батл репорт, фейловый',
            'mission': mission.id,
            'rosters': [roster1.id, roster2.id],
            'winners': [roster1.id, roster2.id],
            'layout': '1vs1',
            'deployment': 'dow',
            'comment': u'Первый ростер победил :D'
        }
        count = Report.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        amount = 1
        self.assertContains(
            response,
            unicode(
                _("You can not add more winners than %(amount)s") %
                {'amount': amount}
            )
        )

    def test_roster_win_defeats(self):
        report = Report.objects.filter(layout='1vs1')[0]
        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)

        mission = report.mission
        winner = report.winners.all()[0]
        winner = winner.reload_wins_defeats()
        self.assertNotEqual(winner.wins, 0)
        # posting new report
        rosters = [i.pk for i in report.rosters.all()]
        post = {
            'title': u'Новый репорт',
            'mission': mission.id,
            'rosters': rosters,
            'winners': [winner.id, ],
            'layout': '1vs1',
            'deployment': 'dow',
            'comment': u'Новый победный реп'
        }
        count = Report.objects.count()
        url = reverse('tabletop:report-add')
        response = self.client.post(url, post, follow=True)
        report = Report.objects.all()[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count + 1, Report.objects.count())
        wins = winner.wins
        winner = Roster.objects.get(pk=winner.pk)
        self.assertEqual(report.approved, False)
        self.assertEqual(winner.wins, wins)
        approve_url = reverse('tabletop:report-approve', args=(report.pk, ))
        self.client.login(username='admin', password='123456')
        response = self.client.get(approve_url, follow=True)
        self.assertEqual(response.status_code, 200)
        winner = Roster.objects.get(pk=winner.pk)
        self.assertEqual(winner.wins, wins + 1)


class RosterTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_games.json',
        'tests/fixtures/load_missions.json',
        'tests/fixtures/load_codexes.json',
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

    def test_roster_delete(self):
        roster = self.add_roster()
        self.login(user=roster.owner.username)
        response = self.client.post(roster.get_delete_url(), {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Roster.objects.filter(pk=roster.pk).exists(), False)

    def test_roster_delete_failure(self):
        roster = self.add_roster()
        self.login(user='admin')
        response = self.client.post(roster.get_delete_url(), {}, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Roster.objects.filter(pk=roster.pk).exists(), True)


class CodexTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_universes.json',
        'tests/fixtures/load_sides.json',
        'tests/fixtures/load_armies.json',
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

    def test_codex_create_failure(self):
        self.login('user')
        count = Codex.objects.count()
        url = reverse('tabletop:codex-add')
        response = self.client.post(url, self.post, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Codex.objects.count(), count)

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

    def test_codex_delete(self):
        codex = self.add_codex()
        self.login('admin')
        count = Codex.objects.count()
        url = codex.get_delete_url()
        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Codex.objects.count(), count - 1)
        self.assertEqual(Codex.objects.filter(pk=codex.pk).exists(), False)

    def test_codex_delete_failure(self):
        codex = self.add_codex()
        self.login('user')
        count = Codex.objects.count()
        url = codex.get_delete_url()
        response = self.client.post(url, {}, follow=True)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Codex.objects.count(), count)
        self.assertEqual(Codex.objects.filter(pk=codex.pk).exists(), True)


class ReportTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_games.json',
        'tests/fixtures/load_missions.json',
        'tests/fixtures/load_armies.json',
        'tests/fixtures/load_sides.json',
        'tests/fixtures/load_codexes.json',
        'tests/fixtures/load_rosters.json',
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

    def test_report_anonymous_create(self):
        response = self.client.post(self.create_url, self.post, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_report_anonymous_update(self):
        report = self.add_report()
        response = self.client.post(report.get_edit_url(), self.post,
                                    follow=True)
        self.assertEqual(response.status_code, 404)

    def test_report_anonymous_delete(self):
        report = self.add_report()
        response = self.client.post(report.get_delete_url(), {},
                                    follow=True)
        self.assertEqual(response.status_code, 404)

    def test_report_list(self):
        self.add_report()
        url = reverse('tabletop:report-list')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('object_list', context)
        self.assertEqual(context['object_list'].count(), 1)

    def test_report_get(self):
        report = self.add_report()
        response = self.client.get(report.get_absolute_url(), follow=True)
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('object', context)
        self.assertIsInstance(context['object'], Report)

    def test_report_user_create(self):
        self.login('user')
        count = Report.objects.count()
        response = self.client.post(self.create_url, self.post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        self.assertEqual(Report.objects.count(), count + 1)
        report = Report.objects.latest('pk')
        self.assertEqual(report.owner, self.user)

    def test_report_user_update(self):
        report = self.add_report(user=self.user)
        self.login('user')
        response = self.client.post(report.get_edit_url(), self.post_update,
                                    follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        report = Report.objects.get(pk=report.pk)
        self.assertInstance(report, self.post_update)

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

    def test_report_user_update_non_owner(self):
        """ non-owner's can not update/delete reports of non their own """
        report = self.add_report(user=self.admin)
        self.login('user')
        response = self.client.post(report.get_edit_url(), self.post_update,
                                    follow=True)
        self.assertEqual(response.status_code, 403)

    def test_report_user_delete_non_owner(self):
        """ non-owner's can not update/delete reports of non their own """
        report = self.add_report(user=self.admin)
        self.login('user')
        response = self.client.post(report.get_delete_url(), {},
                                    follow=True)
        self.assertEqual(response.status_code, 403)

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
                unicode(_("There's no such winner `%s` in rosters")
                        % winner.__unicode__()),
                form.errors['winners']
            )


class CacheTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_games.json',
        'tests/fixtures/load_missions.json',
        'tests/fixtures/load_codexes.json',
        'tests/fixtures/load_rosters.json',
        'tests/fixtures/load_battle_reports.json'
    ]

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def get_battle_report_cache(self, report):
        return cache.get('tabletop:report:%s' % report.pk)

    def del_battle_report_cache(self, report):
        cache.delete('tabletop:report:%s' % report.pk)

    def test_cache_key_prefix(self):
        self.assertEqual(settings.CACHES['default']['KEY_PREFIX'], 'tests')

    def not_test_battle_report_cache(self):
        report = Report.objects.all()[0]
        # fixture should caches it
        self.assertEqual(self.get_battle_report_cache(report), report)
        self.del_battle_report_cache(report)
        self.assertEqual(self.get_battle_report_cache(report), None)
        report.save()
        self.assertEqual(self.get_battle_report_cache(report), report)
        report.delete()
        self.assertEqual(self.get_battle_report_cache(report), None)