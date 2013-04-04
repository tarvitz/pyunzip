# coding: utf-8
from django.test import TestCase
from apps.core.helpers import (
    post_markup_filter,
) 
from django.core.urlresolvers import reverse
from apps.news.models import News
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.comments.models import Comment

class CodeTest(TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_news_categories.json',
        'tests/fixtures/load_news.json'
    ]
    def setUp(self):
        pass

    def tearDown(self):
        pass

    """ helpers """
    def process_messages(self, instance, kw, fx={}):
        messages = []
        for (key, value) in kw.items():
            try:
                if key in fx:
                    self.assertEqual(getattr(instance, key), fx[key].objects.get(pk=value))
                else:
                    self.assertEqual(getattr(instance, key), value)
            except AssertionError as err:
                messages.append({
                    'err': err,
                    'key': key,
                    'value': value
                })
        return messages

    def create_comment(self):
        n = News.objects.all()[0]
        ct = ContentType.objects.get(
            app_label=n._meta.app_label,
            model=n._meta.module_name
        )
        user = User.objects.get(username='user')
        comment = Comment(
            user=user, comment='user comment',
            content_type=ct, object_pk=n.id, site_id=1
        )
        comment.save()
        return comment

    """ testing helpers module """
    def test_urls(self):
        prefix='core'
        urls = [
            'password-restored',
            'password-restore-initiated',
            'css-db',
            'css-edit',
            'ip-get-address',
            'permission-denied',
            'currently-unavailable',
            'wot_verification',
            'url_robots',
            'subscription',
        ]
        messages = []
        for user in ['user', 'admin', None]:
            if user:
                logged = self.client.login(username=user, password='123456')
                self.assertEqual(logged, True)
            for url in urls:
                _url = reverse('%s:%s' % (prefix, url))
                try:
                    response = self.client.get(_url, follow=True)
                    self.assertEqual(response.status_code, 200)
                except AssertionError as err:
                    messages.append({
                        'err': err,
                        'url': _url,
                        'user': user
                    })
        if messages:
            for msg in messages:
                print "Could not get url %(user)s in %(url)s, got %(err)s" % msg
            raise AssertionError

    def test_post_markup_unicode(self):
        quote_source = u"(Пользователь){цитата}"
        quote = post_markup_filter(quote_source)
        self.assertNotIn(quote_source, quote)

    def test_post_markup(self):
        quote_source = u"(User){quote}"
        quote = post_markup_filter(quote_source)
        self.assertNotIn(quote_source, quote)

    def test_post_markup_variations(self):
        quotes = [
            u'(User){quote\n\n\n\nnquote}',
            u'(User){\n\nq\n\n\ote}',
            u'(User){\na\n}'
        ]
        messages = []
        for (index, quote) in enumerate(quotes):
            try:
                self.assertNotIn(post_markup_filter(quote), quotes[index])
            except AssertionError as err:
                messages.append(err)

        if messages:
            for msg in messages:
                print msg
            raise AssertionError

    def test_submit_comment(self):
        # anonymous could not post comments
        url = reverse('core:comment-add')
        n = News.objects.all()[0]
        ct = ContentType.objects.get(
            app_label=n._meta.app_label,
            model=n._meta.module_name
        )

        post = {
            'content_type': ct.pk,
            'object_pk': str(n.pk),
            'syntax': 'textile',
            'comment': 'The faith without deeds is worthless'
        }

        count = Comment.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertEqual(count, Comment.objects.count())
        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.filter(user__username='user', comment=post['comment'])
        self.assertNotEqual(comment.count, 0)
        comment = comment[0]
        messages = self.process_messages(comment, post, fx={'content_type': ContentType})

        if messages:
            for msg in messages:
                print "Got error saving with %(key)s, %(err)s" % msg
            raise AssertionError

    def test_posting_comment_twice(self):
        # deny of twice posting, just ignore second one
        logged = self.client.login(username='user', password='123456')
        self.assertEqual(logged, True)

        url = reverse('core:comment-add')
        n = News.objects.all()[0]
        ct = ContentType.objects.get(
            app_label=n._meta.app_label,
            model=n._meta.module_name
        )

        post = {
            'content_type': ct.pk,
            'object_pk': str(n.pk),
            'syntax': 'textile',
            'comment': 'The faith without deeds is worthless'
        }
        count = Comment.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(count + 1, Comment.objects.count())

        # do not create another object just ignore
        for i in range(10):
            response = self.client.post(url, post, follow=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(count + 1, Comment.objects.count())
            comment = Comment.objects.all()[0]
            self.assertEqual(comment.comment, post['comment'])
        # but we can append another data
        post.update({'comment': 'Faith is internal'})

        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count + 1, Comment.objects.count())
        comment = Comment.objects.order_by('-submit_date')[0]
        # test for information append, not overwrite!
        self.assertIn(post['comment'], comment.comment)
        self.assertNotEqual(comment, comment.comment)

        # admin can post the same comment
        logged = self.client.login(username='admin', password='123456')
        self.assertEqual(logged, True)
        count = Comment.objects.count()
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count + 1, Comment.objects.count())
        # than user can post new comment with the same text, it's not
        # restricted
        self.client.login(username='user', password='123456')
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count + 2, Comment.objects.count())
        last_comment = Comment.objects.order_by('-submit_date')[0]
        self.assertEqual(last_comment.comment, post['comment'])
        self.assertEqual(last_comment.user.username, 'user')

    def test_admin_edit_comment(self):
        self.client.login(username='admin', password='123456')
        comment = self.create_comment()
        post = {
            'comment': 'Admin edit and on',
            'content_type': comment.content_type.pk,
            'object_pk': comment.object_pk
        }
        url = reverse('core:comment-edit', args=(comment.id, ))
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(id=comment.id)
        self.assertEqual(comment.comment, post['comment'])


    def test_admin_purge_comment(self):
        comment = self.create_comment()
        self.client.login(username='admin', password='123456')
        url = reverse('core:comment-purge', args=(comment.id, 'approve'))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.filter(id=comment.id)
        self.assertEqual(len(comment), 0)


    def test_admin_hide_comment(self):
        comment = self.create_comment()
        self.client.login(username='admin', password='123456')
        url = reverse('core:comment-del-restore', args=(comment.id, 'delete'))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(id=comment.id)
        self.assertEqual(comment.is_removed, True)
        url = reverse('core:comment-del-restore', args=(comment.id, 'restore'))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(id=comment.id)
        self.assertEqual(comment.is_removed, False)

    def test_admin_quick_edit_comment(self):
        comment = self.create_comment()
        self.client.login(username='admin', password='123456')
        url = reverse('core:comment-edit-ajax', args=(comment.id, ))
        post = {
            'comment': 'new comment edit',
            'content_type': comment.content_type.pk,
            'object_pk': comment.object_pk
        }
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(id=comment.id)
        self.assertEqual(comment.comment, post['comment'])

    def test_self_quick_edit_comment(self):
        comment = self.create_comment()
        self.client.login(username='admin', password='123456')
        url = reverse('core:comment-edit-ajax', args=(comment.id, ))
        post = {
            'comment': 'new comment edit',
            'content_type': comment.content_type.pk,
            'object_pk': comment.object_pk
        }
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(id=comment.id)
        self.assertEqual(comment.comment, post['comment'])

    def test_self_hide_comment(self):
        comment = self.create_comment()
        self.client.login(username='user', password='123456')
        url = reverse('core:comment-del-restore', args=(comment.id, 'delete'))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(id=comment.id)
        self.assertEqual(comment.is_removed, True)
        url = reverse('core:comment-del-restore', args=(comment.id, 'restore'))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(id=comment.id)
        self.assertEqual(comment.is_removed, False)

    def test_self_purge_comment(self):
        comment = self.create_comment()
        self.client.login(username='admin', password='123456')
        url = reverse('core:comment-purge', args=(comment.id, 'approve'))
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.filter(id=comment.id)
        self.assertEqual(len(comment), 0)

    def test_self_edit_comment(self):
        comment = self.create_comment()
        self.client.login(username='user', password='123456')
        url = reverse('core:comment-edit', args=(comment.id, ))
        post = {
            'comment': 'new comment 111',
            'content_type': comment.content_type.pk,
            'object_pk': comment.object_pk
        }
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        comment = Comment.objects.get(id=comment.id)
        self.assertEqual(comment.comment, post['comment'])

    def test_css_edit(self):
        pass

    def test_unsubscribe(self):
        pass

    def test_settings(self):
        pass

    def test_settings_store(self):
        pass
