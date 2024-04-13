from django import template

register = template.Library()

def number_converter(value):
    """
    Convert a number to a string representation with magnitude suffix.

    Args:
        value (int): The number to be converted.

    Returns:
        str: The string representation of the number with magnitude suffix.

    Examples:
        >>> number_converter(1)
        '1'
        >>> number_converter(2500)
        '2.5K'
        >>> number_converter(100000)
        '100K'
        >>> number_converter(1000000)
        '1M'
    """

    value = float('{:.3g}'.format(value))
    magnitude = 0
    while abs(value) >= 1000:
        magnitude += 1
        value /= 1000.0
    return '{}{}'.format('{:f}'.format(value).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


register.filter('number_converter', number_converter)