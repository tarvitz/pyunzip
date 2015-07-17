
from django.template import Context, Template


def preview(value, wc, end_with='..'):
    context = Context({'value': value})
    template = Template('{{ value|truncatewords:%s }}%s' % (wc, end_with))
    return template.render(context)


def preview_html(value, wc, end_with='..'):
    context = Context({'value': value})
    template = Template('{{ value|truncatewords_html:%s }}%s' % (wc, end_with))
    return template.render(context)
