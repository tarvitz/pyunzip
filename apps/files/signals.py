from apps.files.models import Image
from django.db.models.signals import post_save


def image_save(instance, **kwargs):
    return instance


def setup_signals():
    post_save.connect(image_save, sender=Image)
