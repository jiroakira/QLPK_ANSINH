import decimal
from finance.models import HoaDonChuoiKham
from medicine.models import DonThuoc, KeDonThuoc
from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.db import models
from clinic.models import ChuoiKham, TrangThaiChuoiKham
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

today = timezone.localtime(timezone.now())
tomorrow = today + timedelta(1)
today_start = today.replace(hour=0, minute=0, second=0)
today_end = tomorrow.replace(hour=0, minute=0, second=0)

def thanh_toan_don_thuoc(request, *args, **kwargs):
    """ 
        method này được sử dụng khi phòng tài chính muốn thanh toán hóa đơn thuốc cho bệnh nhân
    """ 
    id_don_thuoc = kwargs.get('id', None)
    # nguoi_dung = User.objects.filter(don_thuoc__id=id_don_thuoc)
    don_thuoc = DonThuoc.objects.filter(id=id_don_thuoc)[0]
    danh_sach_thuoc = KeDonThuoc.objects.filter(don_thuoc=don_thuoc)
    tong_tien = []
    for thuoc_instance in danh_sach_thuoc:
        if thuoc_instance.bao_hiem:
            gia = thuoc_instance.thuoc.gia_thuoc.gia * decimal.Decimal((1-(thuoc_instance.thuoc.bao_hiem_thuoc.muc_bao_hiem / 100))) * thuoc_instance.so_luong
        else:
            gia = thuoc_instance.thuoc.gia_thuoc.gia * thuoc_instance.so_luong
        tong_tien.append(gia)
    
    total_spent = sum(tong_tien)
    tong_tien.clear()

    data = {
        'tong_tien': total_spent,
        # 'nguoi_dung': nguoi_dung,
        'don_thuoc': don_thuoc,
        'danh_sach_thuoc': danh_sach_thuoc
    }
    return render(request, 'template.html', context=data)

    # TODO thanh toán hóa đơn thuốc kết hợp với số tiền khấu trừ sau khi áp dụng bảo hiểm

def thanh_toan_dich_vu_kham(request, *args, **kwargs):
    pass

def list_hoa_don_dich_vu(request, *args, **kwargs):
    trang_thai = TrangThaiChuoiKham.objects.get_or_create(trang_thai="Đang chờ")[0]
    hoa_don_dich_vu = HoaDonChuoiKham.objects.filter(thoi_gian_tao__lte=today_end, trang_thai=trang_thai)
    pass
    


