try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
# from django.db.models.signals import post_save


def setup_signals():
    pass