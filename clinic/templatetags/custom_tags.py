from django import template
from django.contrib.auth import get_user_model

User = get_user_model()

register = template.Library()

@register.simple_tag
def danh_sach_bac_si_lam_sang():
    return User.objects.filter(chuc_nang = '3')
