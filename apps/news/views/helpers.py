# coding: utf-8
import os
from apps.core.helpers import render_to
from apps.core.helpers import post_markup_filter, render_filter
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@render_to('helpers/preview/general.html')
def markup_preview(request):
    data = request.POST.get('data', '')
    markup = request.GET.get('markup', None)
    template = request.GET.get('template', None)

    preview = post_markup_filter(data)
    preview = render_filter(preview, markup or 'textile')
    data = {'preview': preview}
    if template:
        data.update({
            '_template': os.path.join('helpers/preview', template + '.html')
        })
    return data
