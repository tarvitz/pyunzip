from apps.files.models import Image
from django.db.models.signals import post_save
from django.conf import settings


def image_save(instance,**kwargs):
    #saving thumbnail
    if settings.USE_OLD_THUMBNAIL_IMAGE_SCHEME:
        if instance.image:
            if instance.thumbnail:
                return instance
            instance.generate_thumbnail()
            instance.save()
            
def setup_signals():
    post_save.connect(image_save,sender=Image)
