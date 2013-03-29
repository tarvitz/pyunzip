# coding: utf-8
from django.test import TestCase
from apps.core.helpers import (
    post_markup_filter,
) 
from django.core.urlresolvers import reverse
from apps.news.models import News
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

    """ testing helpers module """
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
        response = self.client.post(url, post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(count + 1, Comment.objects.count())
        comment = Comment.objects.all()[0]
        self.assertEqual(comment.comment, post['comment'])