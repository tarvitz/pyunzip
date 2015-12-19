# coding: utf-8
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from . import models


admin.site.register(models.UserSID)
admin.site.site_header = _("Tessera admin")
admin.site.site_title = _("Tessera")
