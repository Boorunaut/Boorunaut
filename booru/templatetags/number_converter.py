import re
from datetime import date, datetime
from decimal import Decimal

from django import template
from django.conf import settings
from django.template import defaultfilters
from django.utils.formats import number_format
from django.utils.safestring import mark_safe
from django.utils.timezone import is_aware, utc
from django.utils.translation import gettext as _, ngettext, pgettext

register = template.Library()


# A tuple of standard large number to their converters
number_converter_converters = (
    (3, lambda number: (
        ngettext('%(value).1f k', '%(value).1f k', number),
        ngettext('%(value)s k', '%(value)s k', number),
    )),
    (6, lambda number: (
        ngettext('%(value).1f M', '%(value).1f M', number),
        ngettext('%(value)s M', '%(value)s M', number),
    )),
    (9, lambda number: (
        ngettext('%(value).1f B', '%(value).1f B', number),
        ngettext('%(value)s B', '%(value)s B', number),
    ))
)


@register.filter(is_safe=False)
def number_converter(value):
    """
    Convert a large integer to a friendly text representation. Based directly in intword,
    but converts to k, M, and B.
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    if value < 999:
        return value

    def _check_for_i18n(value, float_formatted, string_formatted):
        """
        Use the i18n enabled defaultfilters.floatformat if possible
        """
        if settings.USE_L10N:
            value = defaultfilters.floatformat(value, 1)
            template = string_formatted
        else:
            template = float_formatted
        return template % {'value': value}

    for exponent, converters in number_converter_converters:
        large_number = 10 ** exponent
        if value < large_number * 1000:
            new_value = value / large_number
            return _check_for_i18n(new_value, *converters(new_value))
    return value
