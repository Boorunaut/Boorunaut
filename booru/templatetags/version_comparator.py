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

from booru.utils import compare_strings

register = template.Library()

@register.inclusion_tag('booru/templatetags/version_comparator.html')
def version_comparator(current_version, field_name):
    previous_version = current_version.prev_record

    current_value = getattr(current_version, field_name)    
    
    if previous_version != None:
        previous_value = getattr(previous_version, field_name)
    else:
        previous_value = ""

    result = compare_strings(previous_value, current_value)
    return {"value": result}