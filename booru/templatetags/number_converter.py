from django import template

register = template.Library()

def number_converter(value):
    magnitude = 0
    while abs(value) >= 1000:
        magnitude += 1
        value /= 1000.0
    return '%.1f%s' % (value, ['', 'K', 'M', 'B', 'T'][magnitude])

register.filter('number_converter', number_converter)