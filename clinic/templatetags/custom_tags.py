from django import template
from django.contrib.auth import get_user_model

User = get_user_model()

register = template.Library()

@register.simple_tag
def danh_sach_bac_si_lam_sang():
    return User.objects.filter(chuc_nang = '3')

@register.filter()
def check_permission(user, permission):
    if user.user_permissions.filter(codename = permission).exists():
        return True
    return False