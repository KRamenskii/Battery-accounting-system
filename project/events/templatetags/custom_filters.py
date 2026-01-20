from django import template

register = template.Library()

@register.filter
def after_pipe(value):
    """Возвращает часть строки после '|'"""
    if value and '|' in str(value):
        return str(value).split('|', 1)[1].strip()
    return value

@register.filter
def before_pipe(value):
    """Возвращает часть строки до '|'"""
    if value and '|' in str(value):
        return str(value).split('|', 1)[0].strip()
    return value