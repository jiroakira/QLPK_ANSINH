from clinic.models import TinhTrangPhongKham
from django.contrib import admin
from .models import (
    BaiDang, ChiSoXetNghiem, ChiTietChiSoXetNghiem, 
    ChuoiKham, DanhMucBenh, DanhMucChuongBenh, DanhMucKhoa, DanhMucLoaiBenh, DanhMucNhomBenh, 
    DichVuKham, District, DoTuoiXetNghiem, DoiTuongXetNghiem, 
    FileKetQua, 
    FileKetQuaChuyenKhoa, 
    FileKetQuaTongQuat, FilePhongKham, GoiThau, HtmlKetQua,  
    KetQuaChuyenKhoa, 
    KetQuaTongQuat, KetQuaXetNghiem, 
    LichHenKham, LichSuChuoiKham, MauPhieu, NhomChiPhi, NhomTaiNan,
    PhanKhoaKham, 
    PhongChucNang, 
    PhongKham, Province, 
    TrangThaiChuoiKham, 
    TrangThaiKhoaKham, 
    TrangThaiLichHen, 
    User, 
    BacSi, Ward
)

from django.contrib.auth.models import Permission

class DichVuKhamAdmin(admin.ModelAdmin):
    search_fields = ('ten_dvkt',)



admin.site.register(User)
admin.site.register(PhongChucNang)
admin.site.register(LichHenKham)
admin.site.register(TrangThaiLichHen)
admin.site.register(PhanKhoaKham)
admin.site.register(ChuoiKham)
admin.site.register(KetQuaTongQuat)
admin.site.register(KetQuaChuyenKhoa)
admin.site.register(FileKetQua)
admin.site.register(DichVuKham, DichVuKhamAdmin)
admin.site.register(TrangThaiChuoiKham)
admin.site.register(TrangThaiKhoaKham)
admin.site.register(FileKetQuaTongQuat)
admin.site.register(FileKetQuaChuyenKhoa)
admin.site.register(BaiDang)
admin.site.register(BacSi)
admin.site.register(PhongKham)
admin.site.register(TinhTrangPhongKham)
admin.site.register(ChiSoXetNghiem)
admin.site.register(ChiTietChiSoXetNghiem)
admin.site.register(DoiTuongXetNghiem)
admin.site.register(DoTuoiXetNghiem)
admin.site.register(KetQuaXetNghiem)
admin.site.register(FilePhongKham)
admin.site.register(DanhMucChuongBenh)
admin.site.register(DanhMucNhomBenh)
admin.site.register(DanhMucLoaiBenh)
admin.site.register(DanhMucBenh)
admin.site.register(NhomChiPhi)
admin.site.register(NhomTaiNan)
admin.site.register(DanhMucKhoa)
admin.site.register(GoiThau)
admin.site.register(MauPhieu)
admin.site.register(HtmlKetQua)
admin.site.register(Province)
admin.site.register(District)
admin.site.register(Ward)
admin.site.register(Permission)
admin.site.register(LichSuChuoiKham)