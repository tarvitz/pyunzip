# coding: utf-8
from django.db.models.signals import (
    pre_save, post_save, pre_delete
)

__all__ = [
]


#@receiver(pre_save, sender=CoursePage)
#def course_page_pre_saved(instance, **kwargs):
#   pass

def setup_run():
    pass
