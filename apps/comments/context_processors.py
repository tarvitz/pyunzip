# coding: utf-8
from apps.comments.models import CommentWatch


def comment_watches(request):
    comment_watch = CommentWatch.objects.none()
    if request.user.is_authenticated():
        comment_watch = CommentWatch.objects.filter(
            is_updated=True, is_disabled=False,
            user=request.user
        )

    return {
        'comment_watches': comment_watch,
    }