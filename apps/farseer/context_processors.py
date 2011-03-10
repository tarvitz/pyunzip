from apps.core import get_skin_template
from apps.core.helpers import get_settings
from apps.farseer.models import Discount
from django.template.loader import get_template, TemplateDoesNotExist

def steam_discounts(request):
    return {'steam_discounts':Discount.objects.all()}
