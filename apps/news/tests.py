# coding: utf-8
#from django.utils import unittest
from django.test import TestCase
from apps.news.models import Category, News
from django.contrib.auth.models import User
#from django.test.client import RequestFactory, Client
from django.core.urlresolvers import reverse

class JustTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
        'tests/fixtures/load_news.json',
    ]

    def setUp(self):
        self.urls_void = [
            "/news/",
            '/news/archived/',
            '/markup/preview/',
            '/article/created/'
        ]
        self.urls_registered = [
            '/article/add/',  # 302
            "/news/user/",  # 302
        ]
        self.urls_302 = [

        ]

    def test_urls_anonymous(self):
        self.client.logout()
        messages = []
        for url in self.urls_registered:
            response = self.client.get(url)
            try:
                self.assertEqual(response.status_code, 302)
            except AssertionError as err:
                messages.append({'url': url, 'err': err})
        if messages:
            for msg in messages:
                print "URL: %(url)s failed with: %(err)s" % msg
            raise AssertionError

    def test_urls_generic(self):
        messages = []

        for url in self.urls_void:
            response = self.client.get(url)
            try:
                self.assertEqual(response.status_code, 200)
            except AssertionError as err:
                messages.append({'err': err, 'url': url})
        if messages:
            for msg in messages:
                print "URL: %(url)s failed with: %(err)s" % msg
            print "=" * 10
            raise AssertionError
        messages = []
        for url in self.urls_302:
            response = self.client.get(url)
            try:
                self.assertEqual(response.status_code, 302)
            except AssertionError as err:
                messages.append({'err': err, 'url': url})
        for msg in messages:
            print "URL: %(url)s failed with: %(err)s" % msg
        if messages:
            print "=" * 10
            raise AssertionError

    def test_user_login(self):
        #import ipdb
        #ipdb.set_trace()
        pass

    def test_urls_user(self):
        loggined = self.client.login(username='user', password='123456')
        self.assertEqual(loggined, True)
        self.test_urls_generic()

    def test_urls_admin(self):
        loggined = self.client.login(username='admin', password='123456')
        self.assertEqual(loggined, True)
        self.test_urls_generic()

    def test_news_post_anonymous(self):
        self.client.logout()
        category = Category.objects.get()
        count = News.objects.count()
        post = {
            'title': u'Заголовок',
            'author': '',  # blank means poster user
            'category': category.id,
            'content': u'Новость 1',
            'syntax': 'textile',
            'url': '',
        }
        response = self.client.post(
            reverse('news:article-add'), post, follow=True
        )
        new_count = News.objects.count()
        self.assertNotEqual(count + 1, new_count)

    def test_news_post_user(self):
        """
        user posts article without approval
        """
        self.client.login(username='user', password='123456')
        user = User.objects.get(username='user')

        category = Category.objects.get()
        count = News.objects.count()
        post = {
            'title': u'Заголовок',
            'author': '',  # blank means poster user
            'category': category.id,
            'content': u'Новость 1',
            'syntax': 'textile',
            'url': '',
        }

        response = self.client.post(
            reverse('news:article-add'), post, follow=True
        )

        new_count = News.objects.count()
        self.assertEqual(count + 1, new_count)
        article = News.objects.order_by('-id')[0]

        post.update({
            'category': category,
            'author': user.username
        })
        for (key, value) in post.items():
            self.assertEqual(getattr(article, key), value)
        self.assertEqual(article.approved, False)

    def test_news_post_super_user(self):
        """ superuser posts article with approval """
        username = 'admin'
        self.client.login(username=username, password='123456')
        user = User.objects.get(username=username)
        category = Category.objects.get()
        count = News.objects.count()
        post = {
            'title': u'Заголовок',
            'author': '',  # blank means poster user
            'category': category.id,
            'content': u'Новость 2',
            'syntax': 'textile',
            'url': '',
        }
        response = self.client.post(
            reverse('news:article-add'), post, follow=True
        )
        new_count = News.objects.count()
        self.assertEqual(count + 1, new_count)
        article = News.objects.order_by('-id')[0]

        post.update({
            'category': category,
            'author': user.username
        })
        for (key, value) in post.items():
            self.assertEqual(getattr(article, key), value)
        self.assertEqual(article.approved, True)

    def test_news_user_actions(self):
        """
        user can not approve or disapprove articles
        """
        username = 'user'
        self.client.login(username=username, password='123456')
        count = News.objects.count()
        category = Category.objects.get()
        post = {
            'title': u'Заголовок', 'author': '',
            # blank means poster user
            'category': category.id, 'content': u'Новость 2',
            'syntax': 'textile', 'url': '',
        }
        response = self.client.post(reverse('news:article-add'), post, follow=True)
        new_count = News.objects.count()
        article = News.objects.order_by('-id')[0]
        self.assertEqual(count + 1, new_count)
        response = self.client.get(
            reverse('news:article-action', args=(article.id, 'approve'))
        )
        self.assertEqual(response.status_code, 404)
        article = News.objects.get(pk=article.pk)
        self.assertNotEqual(article.approved, True)
        article.approved = True
        article.save()

        response = self.client.get(
            reverse('news:article-action', args=(article.id, 'unapprove'))
        )
        article = News.objects.get(pk=article.pk)
        self.assertNotEqual(article.approved, False)

    def test_admin_user_actions(self):
        """
        admin can approve or disapprove articles
        """
        username = 'admin'
        self.client.login(username=username, password='123456')
        count = News.objects.count()
        category = Category.objects.get()
        post = {
            'title': u'Заголовок', 'author': '',
            # blank means poster user
            'category': category.id, 'content': u'Новость 2',
            'syntax': 'textile', 'url': '',
            }
        response = self.client.post(reverse('news:article-add'), post, follow=True)
        new_count = News.objects.count()
        article = News.objects.order_by('-id')[0]
        self.assertEqual(count + 1, new_count)
        response = self.client.get(
            reverse('news:article-action', args=(article.id, 'approve')),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        article = News.objects.get(pk=article.pk)
        self.assertEqual(article.approved, True)
        article.approved = True
        article.save()

        response = self.client.get(
            reverse('news:article-action', args=(article.id, 'unapprove')),
            follow=True
        )
        article = News.objects.get(pk=article.pk)
        self.assertEqual(article.approved, False)

    def test_news_edit(self):
        # user can not edit articles that do not belong to him
        # admin can edit any article
        # anonymous can not edit articles at all
        self.client.logout()
        article = News.objects.exclude(owner__username='user')[0]
        edit = {
            'title': u'Новый заголовок',
            'content': u'Новый контент',
            #'author': article.author,  # blank means poster user
            #'syntax': article.syntax,
            #'url': article.url,
        }
        post = dict(category=article.category.id, **edit)
        url = reverse('news:article-edit', args=(article.id, ))
        # anonymous can not edit any news
        self.client.post(url, post, follow=True)
        article = News.objects.get(pk=article.pk)
        for (key, value) in edit.items():
            self.assertNotEqual(getattr(article, key), value)

        # user can not edit news not of his own
        response = self.client.post(url, post, follow=True)
        for (key, value) in edit.items():
            self.assertNotEqual(getattr(article, key), value)

        # admin can edit any news
        logged_in = self.client.login(username='admin', password='123456')
        self.assertEqual(logged_in, True)
        response = self.client.post(url, post, follow=True)
        article = News.objects.get(pk=article.pk)
        for (key, value) in edit.items():
            self.assertEqual(getattr(article, key), value)

        # reset data for user checks
        article.title = 'Radom data here'
        article.content = 'Random content here'
        article.save()

        # user can edit his news but only if their are unapproved!
        self.client.login(username='user', password='123456')
        article = News.objects.filter(owner__username='user', approved=True)[0]
        url = reverse('news:article-edit', args=(article.id,))
        post = dict(category=article.category.id, **edit)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 404)

        article = News.objects.get(pk=article.pk)
        for (key, value) in edit.items():
            self.assertNotEqual(getattr(article, key), value)

        # user can edit his news only if their are unapproved
        article = News.objects.filter(owner__username='user', approved=False)[0]
        url = reverse('news:article-edit', args=(article.pk, ))
        post = dict(category=article.category.id, **edit)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        article = News.objects.get(pk=article.pk)
        for (key, value) in edit.items():
            self.assertEqual(getattr(article, key), value)