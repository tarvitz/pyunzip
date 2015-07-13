# coding: utf-8
#from django.utils import unittest
import os
from django.test import TestCase
from apps.files.models import UserFile
from apps.core.helpers import model_json_encoder
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse
from django.conf import settings
import simplejson as json

import allure
from allure.constants import Severity


@allure.feature("Files")
class JustTest(TestCase):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_rank_types.json',
        'load_ranks.json',
        'load_users.json',
    ]

    def setUp(self):
        self.request_factory = RequestFactory()
        self.urls_void = [

        ]
        self.urls_registered = [

        ]
        self.urls_302 = [

        ]
        self.urls_params = [

        ]
        self.unlink_files = []

    def tearDown(self):
        for unlink in self.unlink_files:
            try:
                os.unlink(unlink)
            except OSError:
                pass

    def print_form_errors(self, form):
        if 'errors' in form:
            for (key, items) in form['errors'].items():
                print(
                    "%(key)s: %(items)s" % {
                        'key': key,
                        'items': ", ".join(items)
                    }
                )

    def no_test_urls_params(self):
        messages = []
        for user in ('user', 'admin', None):
            if user:
                self.client.login(username=user, password='123456')
            else:
                self.client.logout()
            for url in self.urls_params:
                response = self.client.get(url)
                try:
                    self.assertEqual(response.status_code, 200)
                except AssertionError as err:
                    messages.append({'url': url, 'user': user, 'err': err})
        if messages:
            for msg in messages:
                print(
                    "Got error in (%s): %s, with %s" % (
                        msg['user'], msg['url'], msg['err']
                    )
                )
            raise AssertionError

    @allure.story('upload')
    @allure.severity(Severity.NORMAL)
    def test_jquery_file_upload(self):
        the_file = open('tests/fixtures/avatar.png', 'rb')
        post = {
            'title': 'avatar',
            'file': the_file
        }
        # anonymous is not allow to upload
        url = reverse('files:file-upload')
        count = UserFile.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count, UserFile.objects.count())

        # user can upload files normally
        the_file.seek(0)
        post.update({'file': the_file})
        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        js = json.loads(response.content)
        if 'form' in js:
            self.print_form_errors(js['form'])

        self.assertEqual(response.status_code, 200)

        self.assertEqual(count + 1, UserFile.objects.count())
        user_file = UserFile.objects.all()[0]
        path = os.path.join(settings.MEDIA_ROOT, user_file.file.path)
        os.lstat(path)
        self.assertEqual(user_file.plain_type, 'image/png')
        self.assertEqual(user_file.size, user_file.file.size)
        self.unlink_files.append(user_file.file.path)

    @allure.story('delete')
    @allure.severity(Severity.NORMAL)
    def test_delete_file(self):
        self.test_jquery_file_upload()
        self.client.login(username='user', password='123456')
        count = UserFile.objects.filter(owner__username='user').count()
        user_file = UserFile.objects.filter(owner__username='user')[0]
        url = user_file.get_delete_url()
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            count - 1,
            UserFile.objects.filter(owner__username='user').count()
        )
        self.assertEqual(os.path.exists(user_file.file.path), False)

    @allure.story('get')
    @allure.severity(Severity.NORMAL)
    def test_serialize_userfile(self):
        self.client.login(username='user', password='123456')
        post = {
            'title': 'avatar',
            'file': open('tests/fixtures/avatar.png', 'rb')
        }
        url = reverse('files:file-upload')
        count = UserFile.objects.filter(owner__username='user').count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        js = json.loads(response.content)
        if 'form' in js:
            self.print_form_errors(js['form'])
        new_count = UserFile.objects.filter(owner__username='user').count()

        print("\nGot file instance: %s\n" % js['file'])
        self.assertIn('avatar', js['file']['url'])
        self.assertEqual(count + 1, new_count)
        user_file = UserFile.objects.filter(owner__username='user')[0]
        js_file = json.dumps(user_file, default=model_json_encoder)
        self.assertIn(user_file.file.name, js_file)
        self.assertNotEqual(js['thumbnail'], {})
        self.assertIn('url', js['thumbnail'].keys())
        self.unlink_files.append(user_file.file.path)

    @allure.story('upload')
    @allure.severity(Severity.NORMAL)
    def test_big_file_uploading(self):
        self.client.login(username='user', password='123456')
        post = {
            'title': 'big file',
            'file': open('tests/fixtures/big_file.zip', 'rb')
        }
        url = reverse('files:file-upload')
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get('Content-Type'), 'application/json')
        js = json.loads(response.content)
        self.assertIn('form', js)
        self.assertIn('errors', js['form'])
