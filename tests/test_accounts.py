# coding: utf-8
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

class TestUserAccounts(TestCase):
    #fixtures = [
    #    'tests/fixtures/load_accounts.json',
    #] #fixtures are here
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_login(self):
        self.assertEqual(0, 0)
