# coding: utf-8
from django import forms


class RequestFormMixin(object):
    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(RequestFormMixin, self).__init__(*args, **kwargs)


class RequestModelForm(RequestFormMixin, forms.ModelForm):
    pass


class RequestForm(RequestFormMixin, forms.Form):
    pass
