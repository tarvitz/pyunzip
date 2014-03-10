from apps.accounts.models import User
from tastypie.test import ResourceTestCase


class UserResourceTest(ResourceTestCase):
    # Use ``fixtures`` & ``urls`` as normal. See Django's ``TestCase``
    # documentation for the gory details.
    fixtures = ['load_users.json']

    def setUp(self):
        super(UserResourceTest, self).setUp()