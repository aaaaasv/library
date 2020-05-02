from django import template
register = template.Library()

@register.filter
def get_status_color(status):
    colors = {'A': '#00FF7F', 'N': 'red', 'available':'#00FF7F'}
    return colors[status]


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()