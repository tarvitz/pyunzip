from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.comments.models import Comment
from apps.core.helpers import send_notification

"""
def announcement_saved(instance, **kwargs):
    pass
"""
#comment object has user attr that contains user object, passing it as
#current user to prevent self-mail-messaging
def comment_saved(instance, **kwargs):
    #send_notification(instance,kwargs={'user_field':'user','content_field':'get_content'})
    pass

def setup_signals():
    #post_save.connect(announcement_saved,sender=Announcement)
    post_save.connect(comment_saved,sender=Comment)
