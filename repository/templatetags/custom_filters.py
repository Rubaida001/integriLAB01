from django import template

register = template.Library()

@register.filter
def get_last_item(value):
    """
    Split the string by '/' and return the last item.
    """
    if isinstance(value, str):
        return value.split('/')[-1]
    return value
