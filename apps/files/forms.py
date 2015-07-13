from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model
User = get_user_model()

from apps.files.models import Image as ModelImage, UserFile
from apps.core.forms import RequestModelForm

from django.db.models import Sum
from django.conf import settings
from sorl.thumbnail import get_thumbnail
import logging
logger = logging.getLogger(__name__)


class UploadFileForm(RequestModelForm):
    def clean(self):
        if not self.request.user.is_authenticated():
            msg = _("Not authorized")
            self._errors['file'] = ErrorList([msg])
            return self.cleaned_data
        size = self.request.user.files.all().aggregate(Sum('size'))
        # size = size.items()[0][1] or 0
        size = size.get('size__sum') or 0

        size += self.files['file'].size
        if size > settings.USER_FILES_LIMIT:
            msg = _(
                "You are exceeded the limits, "
                "please visit your files page and delete the old ones"
            )
            self._errors['file'] = ErrorList([msg])
            return self.cleaned_data
        return self.cleaned_data

    def save(self, commit=True):
        self.instance.owner = self.request.user
        self.instance.plain_type = self.files['file'].content_type
        self.instance.size = self.files['file'].size
        instance = super(UploadFileForm, self).save(commit=commit)
        if 'image' in instance.plain_type:
            thumb = get_thumbnail(
                instance.file, settings.IMAGE_THUMBNAIL_SIZE, quality=95)
            self.cleaned_data['thumbnail'] = thumb
        return instance

    class Meta:
        model = UserFile
        fields = ('file', 'title')


class GalleryImageForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        attrs = {'class': 'form-control'}
        model = ModelImage
        fields = ('title', 'gallery', 'comments', 'image')
        widgets = {
            'title': forms.TextInput(attrs=attrs),
            'gallery': forms.Select(attrs=attrs),
            'comments': forms.Textarea(attrs=attrs),
        }


class GalleryImageUpdateForm(GalleryImageForm):
    class Meta:
        attrs = {'class': 'form-control'}
        model = ModelImage
        fields = ('title', 'comments', )
        widgets = {
            'title': forms.TextInput(attrs=attrs),
            'comments': forms.Textarea(
                attrs={'class': 'form-control'}
            )
        }


class AgreeForm(forms.Form):
    agree = forms.BooleanField(label=_("Yes, I agree"), required=True)
