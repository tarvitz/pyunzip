# -*- coding: utf-8 -*-
"""
.. module:: apps.tabletop.tests.test_codexes
    :synopsis: Test cases for codexes
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from django.test import TestCase
from apps.tabletop.models import Codex
from apps.core.tests import TestHelperMixin

from apps.wh.models import Army, Side
from apps.core.helpers import get_content_type

from django.core.urlresolvers import reverse

import allure
from allure.constants import Severity


@allure.feature('General: Codexes')
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
