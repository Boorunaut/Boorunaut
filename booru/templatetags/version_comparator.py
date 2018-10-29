import re
from datetime import date, datetime
from decimal import Decimal

from django import template
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template import defaultfilters
from django.utils.formats import number_format
from django.utils.safestring import mark_safe
from django.utils.timezone import is_aware, utc
from django.utils.translation import gettext as _
from django.utils.translation import ngettext, pgettext
from reversion.models import Version

from booru.utils import compare_strings

register = template.Library()

@register.inclusion_tag('booru/templatetags/version_comparator.html')
def version_comparator(model, current_version, field_name):
    versions = Version.objects.get_for_object(model).order_by('revision__date_created')
    version_number = list(versions).index(current_version)

    previous_version = None
    try:
        previous_version = versions[version_number - 1]
    except:
        previous_version = None

    current_value = current_version.field_dict[field_name]

    if type(current_value) == list:
        current_value = ' '.join(str(e) for e in current_value)    

    if previous_version != None:
        previous_value = previous_version.field_dict[field_name]
    else:
        previous_value = ""

    if type(previous_value) == list:
        previous_value = ' '.join(str(e) for e in previous_value)

    # result = compare_strings(previous_value, current_value)
    result = compare_strings(previous_value, current_value)
    return {"value": result}
