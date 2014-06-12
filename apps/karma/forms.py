from apps.karma.models import Karma
from django import forms
from django.utils.translation import ugettext_lazy as _
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    from django.contrib.auth.models import User
from apps.core.helpers import get_object_or_None

ALTER_CHOICES = (
    ('up', _("up")),
    ('down', _('down'))
)


class KarmaForm(forms.Form):
    comment = forms.CharField(
        label=_("Comment"),
        widget=forms.Textarea(
            attrs={'class': 'form-control'}
        ), max_length=512)
    url = forms.URLField(widget=forms.HiddenInput(), required=False)


class KarmaModelForm(forms.ModelForm):
    alter = forms.ChoiceField(
        choices=ALTER_CHOICES, widget=forms.HiddenInput
    )
    user = forms.IntegerField(
        label=_("user"), required=True, widget=forms.HiddenInput
    )
    url = forms.CharField(
        label=_("url"), required=False, widget=forms.HiddenInput
    )

    def clean_user(self):
        user_id = self.cleaned_data['user']
        if not user_id:
            return user_id

        user = get_object_or_None(User, pk=user_id)
        if not user:
            raise forms.ValidationError(_("No such user exists"))
        if user == self.request.user:
            raise forms.ValidationError(_("You can not alter karma for yourself"))
        return user

    def clean(self):
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs['request']
            del kwargs['request']
        super(KarmaModelForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        alter = self.cleaned_data['alter']
        url = self.cleaned_data.get('url')
        if alter == 'up':
            self.instance.value = 1
        elif alter == 'down':
            self.instance.value = -1
        self.instance.voter = self.request.user
        self.instance.url = url
        instance = super(KarmaModelForm, self).save(commit)
        return instance

    class Meta:
        attrs = {'class': 'form-control'}
        model = Karma
        fields = ('comment', 'user', )
        widgets = {
            'user': forms.HiddenInput,
            'comment': forms.Textarea(attrs=attrs)
        }
