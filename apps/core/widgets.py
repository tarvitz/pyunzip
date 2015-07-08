# coding: utf-8

from datetime import date, datetime, time

from django.template.loader import get_template
from django.template import Context

from django import forms
from django.forms import Widget, CheckboxSelectMultiple, CheckboxInput
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.utils import datetime_safe, formats
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_text
from itertools import chain


class TinyMkWidget(Widget):
    def __init__(self,attrs=None):
        default_attrs = {'cols': '40', 'rows': '25'}
        if attrs:
            default_attrs.update(attrs)
        super(TinyMkWidget,self).__init__(default_attrs)

    def render(self,name,value,attrs=None):
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        tinymk_template = get_template('core/widgets/tinymk_widget.html')
        out = tinymk_template.render(Context({'tinymk':final_attrs}))
        out = out+mark_safe(u'<textarea%s>%s</textarea>' % (flatatt(final_attrs),
            conditional_escape(force_text(value))))
        return out


class ChosenSelect(forms.Select):
    def __init__(self, attrs=None):
        default_attrs = {}
        if attrs:
            default_attrs.update(attrs)
        default_attrs.update({'class': 'chzn-select'})
        super(ChosenSelect, self).__init__(default_attrs)


class ChosenSelectMultiple(forms.SelectMultiple):
    def __init__(self, attrs=None):
        default_attrs = {}
        if attrs:
            default_attrs.update(attrs)
        default_attrs.update({'class': 'chzn-select'})
        super(ChosenSelectMultiple, self).__init__(default_attrs)


class CommonDateTimePickerInput(Widget):
    def __init__(self, attrs={}, options={}, format=None):
        self.attrs = {
            'data-date-format': 'YYYY-MM-DD HH:mm',
            'data-toggle': 'datetimepicker',
        }
        self.attrs.update(attrs)
        self.options = options
        if format:
            self.format = format
            self.manual_format = True
        else:
            self.format = formats.get_format('DATETIME_INPUT_FORMATS')[0]
            self.manual_format = False

    def _format_value(self, value):
        if self.is_localized and not self.manual_format:
            return formats.localize_input(value)
        elif hasattr(value, 'strftime'):
            if isinstance(value, datetime):
                value = datetime_safe.new_datetime(value)
            elif isinstance(value, date):
                value = datetime_safe.new_date(value)
            elif isinstance(value, time):
                pass
            else:
                return value
            return value.strftime(self.format)
        return value

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        formatted_value = (
            self._format_value(value)
        )
        rendered = (
            u"<input type='text' name='%(name)s' value='%(value)s' {0}>" % {
                'value': formatted_value or '',
                'name': name
            }
        )
        klass = final_attrs.pop('klass', '')
        flatattrs = flatatt(final_attrs)
        rendered = rendered.format(flatattrs)

        final_attrs.update({
            'element': rendered, 'name': name,
            'value': formatted_value,
            'options': self.options,
            'flat': flatattrs,
            'klass': klass
        })
        node = render_to_string(
            'core/widgets/bootstrap_datetime_picker.html',
            final_attrs,
        )
        return mark_safe(node)


class DateTimePickerInput(CommonDateTimePickerInput):
    def __init__(self, attrs={}, options={}, format=None):
        super(DateTimePickerInput, self).__init__(
            attrs, options, format=format or '%Y-%m-%d %H:%M:%S'
        )


class DatePickerInput(CommonDateTimePickerInput):
    def __init__(self, attrs={}, options={}, format=None):
        super(DatePickerInput, self).__init__(
            attrs, options, format=format or '%Y-%m-%d'
        )
        self.attrs.update({
            'data-date-format': 'YYYY-MM-DD',
            'data-toggle': 'datepicker',
            'data-pick-time': False
        })
        self.attrs.update(attrs)


class TimePickerInput(CommonDateTimePickerInput):
    def __init__(self, format=None, attrs={}, options={}):
        super(TimePickerInput, self).__init__(attrs, options)
        self.format = format or '%H:%M:%S'
        self.attrs.update({
            'data-date-format': 'HH:mm',
            'data-toggle': 'timepicker'
        })
        self.attrs.update(attrs)


class TextHiddenField(Widget):
    def __init__(self, attrs={}):
        self.attrs = attrs

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        # strange behaviour, don't get it wtf
        value = None if value == 'None' else value
        rendered = (
            "<div {0}>%(value)s<input type='hidden'"
            " name='%(name)s' value='%(value)s' {0}></div>"
        ) % {
            'value': escape(value or '') or '',
            'name': name
        }
        rendered = rendered.format(flatatt(final_attrs))
        return mark_safe(rendered)


class DaySelect(CheckboxSelectMultiple):
    def __init__(self, attrs={}):
        self.attrs = attrs

    def render(self, name, value, attrs=None):
        final_attrs = self.build_attrs(attrs)
        final_attrs.update({
            'choices': self.choices,
            'name': name
        })

        node = render_to_string(
            'core/widgets/days_select.html',
            final_attrs,
        )
        return mark_safe(node)

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = [u'<ul>']
        # Normalize to strings
        str_values = set([force_text(v) for v in value])
        out = []
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_text(option_label))
            out.append({
                'label': label_for, 'rendered': rendered_cb,
                'option_label': option_label
            })
        return mark_safe(
            render_to_string("core/widgets/days_select.html", {'items': out})
        )

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
