# coding: utf-8
#from django.utils import unittest
import os
from django.test import TestCase
from apps.tabletop.models import Codex, Roster
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from apps.core.helpers import model_json_encoder
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import simplejson as json

from apps.core.helpers import get_object_or_None


class JustTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_codexes.json',
        'tests/fixtures/load_rosters.json',
    ]

    def setUp(self):
        self.request_factory = RequestFactory()
        self.urls_void = [
            reverse('tabletop:roster', args=(1, )),
            reverse('tabletop:roster', args=(2, )),
            reverse('tabletop:roster', args=(3, ))
        ]
        self.urls_registered = [

        ]
        self.urls_params = [
        ]
        self.unlink_files = []

    def tearDown(self):
        pass

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
                    print "Got %(err)s in %(url)s" % msg
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
            'revision': codex.revisions.split(',')[-1] #last revision
        }

        count = Roster.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, Roster.objects.count())

        # user and admin can post normally
        for user in ('user', 'admin'):
            logged = self.client.login(username=user, password='123456')
            count = Roster.objects.count()
            self.assertEqual(logged, True)
            response = self.client.post(url, post, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(count + 1, Roster.objects.count())