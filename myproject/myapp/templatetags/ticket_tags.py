# your_app/templatetags/ticket_tags.py

from django import template

register = template.Library()

@register.filter
def can_validate(user, ticket):
    # Check if user is a technician and ticket is in 'unaffected' status
    return user.function == 'TECHNICIAN' and ticket.status == 'unaffected'

@register.filter
def can_close(user, ticket):
    # Check if user is in roles that can close the ticket
    return user.function in ["SUPERVISOR"] and ticket.status == 'declared_fixed'

@register.filter
def can_delete(user):
    # Check if user is a superuser or admin
    return user.is_superuser or user.is_staff


@register.filter
def can_return_to_unaffected(user, ticket):
    return user.function in ["SUPERVISOR"] and ticket.status == 'declared_fixed'