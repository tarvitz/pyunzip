from apps.files.models import Image
from django.db.models.signals import post_save


def image_save(instance,**kwargs):
    #saving thumbnail
    if instance.image:
        if instance.thumbnail:
            return instance
        instance.generate_thumbnail()
        instance.save()
            
def setup_signals():
    post_save.connect(image_save,sender=Image)
