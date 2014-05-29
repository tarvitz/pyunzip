try:
    from django.contrib.auth import get_user_model, check_password
    User = get_user_model()
except ImportError:
    from apps.accounts.models import User


class EmailAuthBackend(object):
    """
    Email Authentication backend
    Allows a user to sign in using email/password rather than
    a username/password pair
    """

    def authenticate(self, username=None, password=None):
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
