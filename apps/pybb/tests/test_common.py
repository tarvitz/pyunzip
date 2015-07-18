# coding: utf-8
from apps.accounts.models import User
from django.test import TestCase
from apps.core.tests import TestHelperMixin
from apps.pybb.models import Forum, Topic, Post
from apps.core.helpers import get_object_or_None
from django.core.urlresolvers import reverse
from django.utils.encoding import force_text
import allure
from allure.constants import Severity
from copy import deepcopy


class JustTest(TestCase):
    fixtures = []

    def setUp(self):
        self.urls_void = [
        ]
        self.urls_registered = [
        ]
        self.get_object = get_object_or_None

    def tearDown(self):
        pass

    def check_state(self, instance, data, check=lambda x: x):
        messages = []
        for (key, value) in data.items():
            try:
                check(getattr(instance, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key
                })
        if messages:
            for msg in messages:
                print("Got %(err)s in %(key)s" % msg)
            raise AssertionError


@allure.feature('General: Topics')
class TopicTest(TestHelperMixin, JustTest):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_users.json',
        'load_pybb_categories.json',
        'load_forums.json',
    ]
    add_topic_post = {
        'name': u'Заголовок поста',
        'body': u'Контент поста',
    }

    def setUp(self):
        self.forum = Forum.objects.get(pk=1)

    @allure.story('add')
    @allure.severity(Severity.CRITICAL)
    def test_topic_add(self, role='user'):
        self.login(role)
        url = reverse('pybb:topic-add', args=(self.forum.pk, ))
        count = Topic.objects.count()
        response = self.client.post(url, self.add_topic_post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        self.assertEqual(Topic.objects.count(), count + 1)


@allure.feature('General: Posts')
class PostTest(TestHelperMixin, JustTest):
    fixtures = [
        'load_universes.json',
        'load_fractions.json',
        'load_sides.json',
        'load_armies.json',
        'load_users.json',
        'load_pybb_categories.json',
        'load_forums.json',
        'load_topics.json',
        'load_posts.json',
    ]
    add_post = {
        'body': u'Контент поста',
    }
    edit_post = {
        'body': u'Новый контент поста'
    }

    def setUp(self):
        self.topic = Topic.objects.get(pk=1)
        self.post = Post.objects.get(pk=1)
        self.non_post_owner = User.objects.filter(
            is_superuser=False).exclude(
            username=self.post.user.username)[0]
        # old post copy
        self.post_old_content = deepcopy(self.post)
        self.post_old_content.pk = None
        self.post_old_content.save()

    @allure.story('add')
    @allure.severity(Severity.CRITICAL)
    def test_topic_add_failure(self):
        """ anonymous users can not post """
        url = reverse('pybb:post-add', args=(self.topic.pk, ))
        count = self.topic.posts.count()
        response = self.client.post(url, self.add_post, follow=True)

        self.assertEqual(response.status_code, 404)
        self.proceed_form_errors(response.context)
        self.assertEqual(self.topic.posts.count(), count)

    @allure.story('add')
    @allure.severity(Severity.CRITICAL)
    def test_topic_add(self, role='user'):
        self.login(role)
        url = force_text(reverse('pybb:post-add', args=(self.topic.pk, )))
        count = self.topic.posts.count()
        response = self.client.post(url, self.add_post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        self.assertEqual(self.topic.posts.count(), count + 1)

    @allure.story('add')
    @allure.severity(Severity.CRITICAL)
    def test_topic_add_admin(self, role='admin'):
        self.test_topic_add(role=role)

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_post_update(self, role=None):
        if not role:
            self.login(self.post.user.username)
        elif role in 'anonymous':
            self.logout()
        else:
            self.login(role)
        url = self.post.get_edit_url()
        response = self.client.post(url, self.edit_post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.proceed_form_errors(response.context)
        post = Post.objects.get(pk=self.post.pk)
        self.assertNotEqual(self.post_old_content.body, post.body)
        self.assertEqual(post.body, self.edit_post['body'])

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_post_update_superuser(self):
        self.test_post_update(role='admin')

    @allure.story('update')
    @allure.severity(Severity.CRITICAL)
    def test_post_update_failure(self):
        self.login(self.non_post_owner.username)
        url = self.post.get_edit_url()
        response = self.client.post(url, self.edit_post, follow=True)
        self.assertEqual(response.status_code, 403)
        post = Post.objects.get(pk=self.post.pk)
        self.assertEqual(post.body, self.post_old_content.body)
