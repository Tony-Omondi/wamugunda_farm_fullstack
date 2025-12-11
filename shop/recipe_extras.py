# shop/templatetags/recipe_extras.py
from django import template

register = template.Library()

@register.filter
def total_time(prep, cook):
    try:
        return int(prep or 0) + int(cook or 0)
    except (ValueError, TypeError):
        return 0