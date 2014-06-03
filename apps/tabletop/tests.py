# coding: utf-8
from django.test import TestCase
from apps.tabletop.models import Codex, Roster, Mission, BattleReport
from apps.core.tests import TestHelperMixin
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
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
            #reverse('tabletop:battle-reports-self'),
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
        count = BattleReport.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(count, BattleReport.objects.count())

        # testing for user
        logged = self.client.login(username='user', password='123456')
        user = User.objects.get(username='user')
        self.assertEqual(logged, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        open('file.html', 'w').write(response.content)
        self.assertEqual(count + 1, BattleReport.objects.count())
        report = BattleReport.objects.all()[0]
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
        report = BattleReport.objects.all()[0]
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
            report = BattleReport.objects.get(id=report.id)
            self.check_changes(report, edit, check=self.assertNotEqual)

        edit.update({
            'rosters': [roster1, roster2],
            'winners': [roster2]
        })
        self.client.login(username='admin', password='123456')
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        report = BattleReport.objects.get(id=report.id)
        self.check_changes(report, edit, check=self.assertEqual)

    #@skipIf(True, "broken")
    def test_battle_report_approve_disapprove(self):
        # only admin can approve/disapprove
        self.test_battle_report_add()
        report = BattleReport.objects.all()[0]
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
            report = BattleReport.objects.get(id=report.id)
            self.assertEqual(report.approved, False)
            response = self.client.get(disapprove_url, follow=True)
            if user:
                self.assertEqual(response.status_code, 404)
            else:
                self.assertEqual(response.status_code, 404)
            report = BattleReport.objects.get(id=report.id)
            self.assertEqual(report.approved, False)
        # admin can approve
        self.client.login(username='admin', password='123456')
        report.approved = False
        report.save()
        response = self.client.get(approve_url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = BattleReport.objects.get(id=report.id)
        self.assertEqual(report.approved, True)
        response = self.client.get(disapprove_url, follow=True)
        self.assertEqual(response.status_code, 200)
        report = BattleReport.objects.get(id=report.id)
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
        count = BattleReport.objects.count()
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

    #@skipIf(True, 'broken')
    def test_roster_win_defeats(self):
        report = BattleReport.objects.filter(layout='1vs1')[0]
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
        count = BattleReport.objects.count()
        url = reverse('tabletop:report-add')
        response = self.client.post(url, post, follow=True)
        report = BattleReport.objects.all()[0]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count + 1, BattleReport.objects.count())
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
        report = BattleReport.objects.all()[0]
        # fixture should caches it
        self.assertEqual(self.get_battle_report_cache(report), report)
        self.del_battle_report_cache(report)
        self.assertEqual(self.get_battle_report_cache(report), None)
        report.save()
        self.assertEqual(self.get_battle_report_cache(report), report)
        report.delete()
        self.assertEqual(self.get_battle_report_cache(report), None)