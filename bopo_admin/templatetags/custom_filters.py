import os
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Returns the value for the given key in the dictionary."""
    return dictionary.get(key, "")

@register.filter
def basename(value):
    return os.path.basename(value)