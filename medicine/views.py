from medicine.models import NhomThuoc
from django.shortcuts import render
from django.views import View
from clinic.models import User

def ke_don_thuoc_view(request, **kwargs):
    user_id = kwargs.get('user_id')
    id_chuoi_kham = kwargs.get('id_chuoi_kham')
    benh_nhan = User.objects.get(id = user_id)
    nhom_thuoc = NhomThuoc.objects.all()

    data = {
        'user_id': user_id,
        'id_chuoi_kham': id_chuoi_kham,
        'benh_nhan' : benh_nhan,
        'nhom_thuoc': nhom_thuoc,
    }
    return render(request, 'bac_si_lam_sang/ke_don_thuoc.html', context=data)