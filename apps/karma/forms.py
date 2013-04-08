from apps.karma.models import Karma
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from apps.core.helpers import get_object_or_None

ALTER_CHOICES = (
    ('up', _("up")),
    ('down', _('down'))
)

class AlterKarmaForm(forms.Form):
    #choice = forms.ChoiceField(widget=forms.RadioSelect(),choices=((-1,'+1'),(1,'-1')))
    comment = forms.CharField(widget=forms.Textarea(), max_length=512)
    hidden_nickname = forms.CharField(widget=forms.HiddenInput())
    referer = forms.CharField(widget=forms.HiddenInput())
    url =   forms.CharField(widget=forms.HiddenInput(),required=False)


class KarmaModelForm(forms.ModelForm):
    alter = forms.ChoiceField(
        choices=ALTER_CHOICES, widget=forms.HiddenInput
    )
    user = forms.IntegerField(
        _("user"), required=True, widget=forms.HiddenInput
    )
    url = forms.CharField(
        _("url"), required=False, widget=forms.HiddenInput
    )
    def clean_user(self):
        user_id = self.cleaned_data['user']
        if not user_id:
            return user_id

        user = get_object_or_None(User, pk=user_id)
        if not user:
            raise forms.ValidationError(_("No such user exists"))
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
        model = Karma
        fields = ('comment', 'user', )
        widgets = {
            'user': forms.HiddenInput,
            'comment': forms.Textarea
        }
