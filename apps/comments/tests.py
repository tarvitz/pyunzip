from django.test import TestCase
from apps.core.tests import TestHelperMixin
# Create your tests here.


class CommentWatchTest(TestHelperMixin, TestCase):
    fixtures = [
        'tests/fixtures/load_users.json',
        'tests/fixtures/load_comments.json',
    ]

    def setUp(self):
        pass
