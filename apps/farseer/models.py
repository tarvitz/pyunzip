from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class Discount(models.Model):
    name = models.CharField(_('Game name'),max_length=100)
    price = models.FloatField(_('Price'))
    current_price = models.FloatField(_('Discount'))
    url = models.URLField(_('URL'),max_length=200)

    def __unicode__(self):
        return name
    
    @property
    def discount(self):
        return int(
            100-round(self.current_price/(self.price/100))
        )

