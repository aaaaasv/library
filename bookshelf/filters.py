from django import template
register = template.Library()

@register.filter
def get_status_color(status):
    colors = {'A': '#00FF7F', 'N': 'red', 'available':'#00FF7F'}
    return colors[status]


@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


@register.filter(name='has_reserved')
def has_reserved(user_id, book):
    u_id = int(user_id)
    return book.paperbook.to_giveout.filter(id=u_id).count() > 0