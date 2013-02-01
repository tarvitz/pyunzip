# coding: utf-8
import os
from apps.core.helpers import render_to
from apps.news.templatetags.newsfilters import render_filter
from apps.core.helpers import post_markup_filter, render_filter
from django.utils.safestring import mark_safe


@render_to('helpers/preview/general.html')
def comment_preview(request):
    data = request.POST.get('data', '')
    markup = request.GET.get('markup', None)
    template = request.GET.get('template', None)

    comment = post_markup_filter(data)
    comment = render_filter(comment, markup or 'textile')
    data = {'comment': comment}
    if template:
        data.update({
            '_template': os.path.join('helpers/preview', template  + '.html')
        })

    return data
