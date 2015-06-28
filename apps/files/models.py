import os

from django.contrib.contenttypes import generic
from django.conf import settings
from django.db import models

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError


class Attachment(models.Model):
    attachment = models.FileField(
        _('Attachment'), upload_to=os.path.join(settings.MEDIA_ROOT,
                                                'attachments/'))

    def __unicode__(self):
        return self.attachment.name


class MetaGallery(models.Model):
    gallery_types = [
        ('tech', 'technical'), ('global', 'global'), ('user', 'user')
    ]
    type = models.CharField(_('Type'), choices=gallery_types,
                            max_length=30, null=False)
    name = models.CharField(_('Name'), max_length=100)

    class Meta:
        abstract = True


class Gallery(MetaGallery):
    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('files:galleries', args=(self.pk, ))

    class Meta:
        verbose_name = _('Gallery')
        verbose_name_plural = _('Galleries')


def valid_alias(val):
    if val.replace('_', '').isalnum():
        return val
    raise ValidationError("You should use only letters, digits and _")


class Image(models.Model):
    def upload_to(self, file_name):
        """
        image upload to hander

        :param file_name: file's name
        :rtype: str
        :return: path upload to
        """
        return "images/galleries/%s/%s" % (str(self.owner.id), file_name)

    title = models.CharField(_('Title'), max_length=100)
    alias = models.CharField(
        _('Alias'), max_length=32, blank=True,
        unique=True,
        null=True,
        help_text=_('Fast name to access unit'),
        validators=[valid_alias])  # shorter, wiser
    comments = models.TextField(_('Comments'))
    gallery = models.ForeignKey(Gallery, verbose_name=_("gallery"))
    image = models.ImageField(
        _('Image'), upload_to=upload_to,
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    comment_objects = generic.GenericRelation(
        'comments.Comment',
        object_id_field='object_pk'
    )

    class Meta:
        permissions = (
            ('can_upload', 'Can upload images'),
            ('delete_images', 'Can delete images'),
        )
        verbose_name = _('Image')
        verbose_name_plural = _('Images')
        ordering = ['-id', ]
        
    def get_title(self):
        return self.title

    def get_absolute_url(self):
        return reverse('files:image', args=(self.pk, ))

    def get_edit_url(self):
        return reverse('files:image-edit', args=(self.pk, ))

    def get_delete_url(self):
        return reverse('files:image-delete', args=(self.pk, ))

    def __unicode__(self):
        return "Images"


class UserFile(models.Model):
    def file_upload_to(self, file_name):
        """
        file upload handler

        :param str file_name: file name
        :rtype: str
        :return: path destination
        """
        return "user/%s/files/%s" % (
            str(self.owner.id), file_name
        )

    title = models.CharField(_('title'), max_length=256, blank=True,
                             null=True)
    file = models.FileField(
        _('file'), upload_to=file_upload_to
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='user_file_set')
    plain_type = models.CharField(
        _("plain type"), help_text=_("plain type for "),
        max_length=256, default='octet/stream',
        blank=True, null=True
    )
    actions = []
    size = models.PositiveIntegerField(_('size'), help_text=_('file size'),
                                       default=0)

    def get_file_link(self):
        link = os.path.join(settings.MEDIA_URL, self.file.name)
        name = link[:40] + " ..." if len(link) > 40 else link
        return "<a href='%s'>%s</a>" % (
            link,
            name
        )

    def get_file_name(self):
        if '/' in self.file.name:
            name = self.file.name[self.file.name.rindex('/') + 1:]
            name = name[:40] + " ..." if len(name) > 40 else name
            return name
        return self.file.name

    def get_delete_url(self):
        return reverse('files:file-delete', args=(self.pk,))

    def get_file_size(self):
        try:
            return self.file.size
        except OSError:
            return 0

    def delete(self, *args, **kwargs):
        try:
            os.unlink(self.file.path)
        except OSError:
            pass
        super(UserFile, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.title or "User %s file" % (self.owner.id, )

    class Meta:
        verbose_name = _("User file")
        verbose_name_plural = _("User files")

from apps.files.signals import setup_signals
setup_signals()
