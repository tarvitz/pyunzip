# coding: utf-8
#from django.utils import unittest
from django.test import TestCase
from apps.news.models import Category, News
from django.contrib.auth.models import User
#from django.test.client import RequestFactory, Client
from django.core.urlresolvers import reverse
from apps.core.models import Announcement
from django.contrib.contenttypes.models import ContentType
from apps.core.helpers import get_object_or_None


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
        self.urls_params = [
            reverse('news:news', args=('testing',)),
            reverse('news:article', args=(1,)),
        ]

    def test_urls_params(self):
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
                print "Got error in (%s): %s, with %s" % (
                    msg['user'], msg['url'], msg['err']
                )
            raise AssertionError

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
        self.assertEqual(response.status_code, 200)
        new_count = News.objects.count()
        self.assertNotEqual(count + 1, new_count)

    def test_news_post_user(self):
        # user posts article without approval

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
        url = reverse('news:article-add')
        response = self.client.post(
            url, post, follow=True
        )
        #print "\ntesting: %s\n" % url

        self.assertEqual(response.status_code, 200)
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

        ct = ContentType.objects.get(
            app_label=article._meta.app_label,
            model=article._meta.module_name
        )

        announcement = Announcement.objects.filter(
            object_pk=article.pk, content_type=ct
        )
        self.assertEqual(len(announcement), 1)

    def test_news_post_super_user(self):
        # superuser posts article with approval
        username = 'admin'
        logged = self.client.login(username=username, password='123456')
        self.assertEqual(logged, True)
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
            'approved': True
        }
        response = self.client.post(
            reverse('news:article-add'), post, follow=True
        )
        self.assertEqual(response.status_code, 200)
        new_count = News.objects.count()
        self.assertEqual(count + 1, new_count)
        article = News.objects.order_by('-id')[0]

        post.update({
            'category': category,
            'author': user.username
        })
        messages = []
        for (key, value) in post.items():
            try:
                self.assertEqual(getattr(article, key), value)
            except AssertionError as err:
                messages.append({'err': err, 'key': key})
        if messages:
            for msg in messages:
                print "Got assertion error in %(key)s with %(err)s" % msg
            raise AssertionError
        self.assertEqual(article.approved, True)

        # testing for if not approved
        post.update({
            'approved': False,
            'category': category.id,
            'author': ''
        })
        news_count = News.objects.count()
        response = self.client.post(
            reverse('news:article-add'), post, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(news_count + 1, News.objects.count())
        article = News.objects.order_by('-id')[0]
        messages = []

        post.update({
            'approved': False,
            'category': category,
            'author': user.username
        })
        for (key, value) in post.items():
            try:
                self.assertEqual(getattr(article, key), value)
            except AssertionError as err:
                messages.append({'err': err, 'key': key})
        if messages:
            for msg in messages:
                print "Got assertion error in %(key)s with %(err)s" % msg
            raise AssertionError
        self.assertEqual(article.approved, False)

    def test_news_user_actions(self):
        # user can not approve or disapprove articles

        username = 'user'
        self.client.login(username=username, password='123456')
        count = News.objects.count()
        category = Category.objects.get()
        post = {
            'title': u'Заголовок', 'author': '',
            # blank means poster user
            'category': category.id, 'content': u'Новость 2',
            'syntax': 'textile', 'url': '',
            'approved': True
        }
        response = self.client.post(reverse('news:article-add'), post, follow=True)
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 404)
        article = News.objects.get(pk=article.pk)
        self.assertNotEqual(article.approved, False)

    def test_admin_user_actions(self):
        # admin can approve or disapprove articles

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
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
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
        self.assertEqual(response.status_code, 200)
        for (key, value) in edit.items():
            self.assertNotEqual(getattr(article, key), value)

        # admin can edit any news
        logged_in = self.client.login(username='admin', password='123456')
        self.assertEqual(logged_in, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
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

    def test_article_delete(self):
        # only admin can delete articles
        article = {
            'title': 'deletion',
            'content': 'to delete',
            'syntax': 'textile',
            'author': 'admin',
            'editor': '',
            'category_id': 1,
            'approved': True,
            'owner_id': 1,
        }

        n = News.objects.create(**article)
        # testing deletion with user, no access to delete
        self.client.login(username='user', password='123456')
        url = reverse('news:article-delete', args=(n.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        exists = get_object_or_None(News, pk=n.id)
        self.assertNotEqual(exists, None)

        # deleting by admin
        self.client.login(username='admin', password='123456')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        exists = get_object_or_None(News, pk=n.id)
        self.assertEqual(exists, None)


    def test_article_set_status(self):
        post = {
            'status': 'revision',
            'resend': False,
            'reason': "please make it nice"
        }
        # nobody except admin could set news status
        # testing anonymous
        n = News.objects.filter(approved=False)[0]
        url = reverse('news:article-status-set', args=(n.id, ))
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "login required")
        # checking for user
        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        n = News.objects.get(id=n.id)
        self.assertNotEqual(n.reason, post['reason'])
        # checking for admin
        logged = self.client.login(username='admin', password='123456')
        self.assertEqual(logged, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        n = News.objects.get(id=n.id)
        self.assertEqual(n.reason, post['reason'])
