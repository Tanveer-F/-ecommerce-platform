from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def total_price(items):
    return sum(item.product.price * item.quantity for item in items)
