from django.utils.translation import ugettext_lazy as _, pgettext_lazy


CHOICES = (
    ('', _("Any")),
    (True, pgettext_lazy("is active on select", "Active")),
    (False, pgettext_lazy("is inactive on select", "Inactive"))
)