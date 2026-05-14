from django import template
import html
import re

register = template.Library()

@register.filter
def clean_preview(value):
    if not value:
        return ""
    # Strip HTML tags
    text = re.sub(r'<[^>]+>', '', value)
    # Unescape HTML entities (like &nbsp;)
    text = html.unescape(text)
    return text
