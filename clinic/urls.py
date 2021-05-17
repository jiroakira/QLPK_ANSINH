from clinic.api import DanhSachHoaDonThuocBaoHiem, DanhSachPhongKham
from django.contrib.auth import logout, views as auth_views
from django.db.models import base
from django.views.generic import RedirectView
from medicine.api import ThuocViewSet, CongTyViewSet
from django.urls import path, include
from rest_framework import routers
from .api import (ApiExportBenhNhanBaoHiemExcel, ApiExportExcelDichVu, ApiExportExcelThuoc, ApiListAllGroupOfUser, ApiListGroup, ApiListStaff, ChiTietMauPhieuAPIView, ChuoiKhamGanNhat, ChuoiKhamNguoiDung, ChuoiKhamViewSet,DangKiAPI, DangKiLichHen, DanhSachBacSi, DanhSachBacSi1, DanhSachBaiDang, DanhSachBaoCaoTheoThoiGian, DanhSachBenhNhan, DanhSachBenhNhanChoLamSang, DanhSachBenhNhanListCreateAPIView,DanhSachBenhNhanTheoPhong, DanhSachBenhNhanTheoPhongChucNang,DanhSachChuoiKhamBenhNhan, DanhSachDichVuKhamTheoPhong,DanhSachDichVuTheoPhongChucNang, DanhSachDoanhThuTheoThoiGian,DanhSachDoanhThuDichVu, DanhSachDoanhThuThuoc, DanhSachDonThuocBenhNhan,DanhSachDonThuocDaKe,DanhSachDonThuocPhongThuoc, DanhSachHoaDonDichVu,DanhSachHoaDonThuoc, DanhSachKetQuaChuoiKhamBenhNhan, DanhSachKhamTrongNgay, DanhSachLichHenTheoBenhNhan, DanhSachLichSuKhamBenhNhan, DanhSachMauPhieu, DanhSachNguonCung, DanhSachNhungThuocDuocNhap, DanhSachNhungThuocDuocXuat,DanhSachPhongChucNang, DanhSachThuocNhapDichVu, DanhSachThuocSapHetHan, DanhSachThuocXuatDichVu, DanhSachTieuChuanTheoNhomAPIview, DanhSachVatTu, DanhSachThanhToanLamSang,DanhSachThuocBenhNhan, DanhSachThuocTheoCongTy, DichVuKhamListCreateAPIView, DieuPhoiPhongChucNangView, DoanhThuTheoPhongChucNang,DonThuocGanNhat, FileKetQuaViewSet, FilterBaoHiem, FilterDistrict, FilterWard, GetDanhSachPhanKhoaCuaChuoiKham, GetFuncroomInfo, KetQuaChuoiKhamBenhNhan,KetQuaChuoiKhamBenhNhan2, KetQuaXetNghiemMobile, LichHenKhamViewSet, ListNguoiDungDangKiKham, ListTieuChuanDichVu,PhanKhoaKhamBenhNhan, PhieuKetQuaMobile, PhongChucNangTheoDichVu, SetChiSoDichVuKham, SetChoThanhToan, SetHtmlDichVuKham,SetXacNhanKham, TatCaLichHenBenhNhan, TatCaLichHenBenhNhanList, ThongTinBenhNhanTheoMa,ThongTinPhongChucNang, ThongTinPhongKham, ThuocListCreateAPIView, TimKiemKetQuaBenhNhan, UserInfor, UserViewSet, DichVuKhamViewSet,PhongChucNangViewSet,LichHenKhamSapToi, UserUpdateInfo,UserUpdateInfoRequest, UploadAvatarView,UpdateAppointmentDetail,CapNhatLichHen, HoaDonChuoiKhamNguoiDung, HoaDonChuoiKhamCanThanhToan,HoaDonThuocCanThanhToan, DichVuTheoPhongChucNang, DonThuocCuaChuoiKham, HoaDonThuocCuaChuoiKham, HoaDonDichVuCuaChuoiKham, HoaDonLamSangChuoiKham, HoaDonLamSangGanNhat, DanhSachHoaDonDichVuBaoHiem, DanhSachDoanhThuLamSang, XemDonThuoc, XemLaiBenhNhanDaKhamChuyenKhoaAPIView, XemLaiBenhNhanLamSangAPIView, XuatNhapTongThuocAPIView)
from .views import BatDauChuoiKhamToggle, KetThucChuoiKhamToggle, LoginView, ThanhToanHoaDonDichVuToggle, add_lich_hen, bao_cao_thuoc, bao_cao_xuat_nhap_ton_thuoc_view, bat_dau_chuoi_kham, cap_nhat_thong_tin_bac_si, cap_nhat_thong_tin_benh_nhan, cap_nhat_thong_tin_nhan_vien, cap_nhat_user, changePassword, check_so_dien_thoai_exists, check_username_exists, chi_tiet_bai_dang, chi_tiet_chuoi_kham_benh_nhan, chi_tiet_ket_qua_xet_nghiem, chi_tiet_lich_hen_benh_nhan, chi_tiet_mau_phieu, chi_tiet_phieu_ket_qua, chi_tiet_phieu_ket_qua_lam_sang, chi_tiet_tieu_chuan_dich_vu, chinh_sua_bai_dang, chinh_sua_bai_dang_view, chinh_sua_don_thuoc, chinh_sua_nguon_cung, chinh_sua_phieu_ket_qua_view, chinh_sua_phong_chuc_nang, chinh_sua_thuoc, chinh_sua_thuoc_phong_thuoc, chinh_sua_tieu_chuan_dich_vu, create_bac_si, create_dich_vu, create_don_thuoc_rieng, create_lich_tai_kham, create_mau_hoa_don, create_mau_phieu, create_staff_user, create_tieu_chuan, create_user, create_user_index, dang_ki_tieu_chuan_view, danh_sach_bac_si, danh_sach_bai_dang, danh_sach_benh_nhan, danh_sach_benh_nhan_bao_hiem, danh_sach_benh_nhan_cho, danh_sach_dich_vu_bao_hiem, danh_sach_dich_vu_kham, danh_sach_kham, danh_sach_mau_phieu, danh_sach_phong_chuc_nang, danh_sach_thuoc, danh_sach_thuoc_bao_hiem, danh_sach_thuoc_phong_tai_chinh, danh_sach_thuoc_sap_het_date_view, danh_sach_vat_tu, doanh_thu_phong_kham, don_thuoc, dung_kham, dung_kham_chuyen_khoa, dung_kham_ket_qua_chuyen_khoa, export_dich_vu_bao_hiem_excel, export_excel, export_excel_danh_sach_thuoc_het_date, export_excel_danh_sach_xnt_tong_hop_thuoc, export_thuoc_bao_hiem_excel, files_upload_view, hoa_don_dich_vu, hoa_don_lam_sang, hoa_don_thuoc, hoa_don_tpcn, hoan_thanh_chuoi_kham_hoa_don_thuoc, hoan_thanh_kham, hoan_thanh_kham_hoa_don, import_dich_vu_excel, import_dich_vu_kham_view, import_ma_benh_excel, import_thuoc_excel, import_thuoc_view, import_vat_tu_excel, index, ket_qua_benh_nhan_view, list_tieu_chuan_dich_vu, login, logout_view, menu_view, my_activities, nhan_don_thuoc, nhap_them_thuoc, phan_khoa_kham, phieu_ket_qua, phieu_ket_qua_tong_quat, phong_chuyen_khoa, phong_tai_chinh_danh_sach_cho, phong_thuoc_danh_sach_cho, resetPassword, store_cong_ty, store_dich_vu_kham_excel, store_don_thuoc_rieng, store_ke_don, store_ket_qua_chuyen_khoa_html, store_ket_qua_xet_nghiem, store_nhap_thuoc, store_nhom_quyen, store_phan_khoa, store_thanh_toan_lam_sang, store_thuoc_dich_vu_excel, store_thuoc_excel, store_update_dich_vu_kham, store_update_phieu_ket_qua, store_update_vat_tu, store_uy_quyen, tat_ca_lich_hen_banh_nhan, test_mau_phieu, thay_doi_phan_khoa, thay_doi_phan_khoa_hoa_don_dich_vu, them_bai_dang, them_dich_vu_kham, them_dich_vu_kham_excel, them_ma_benh_excel, them_mau_hoa_don, them_mau_phieu, them_phong_chuc_nang, them_thuoc_excel, them_vat_tu_excel, update_bac_si, update_benh_nhan, update_dich_vu_kham, update_don_thuoc, update_mau_hoa_don, update_mau_phieu, update_nguon_cung, update_nhan_vien, update_nhom_quyen, update_phong_chuc_nang, update_thuoc, update_thuoc_phong_thuoc, update_user, update_vat_tu, upload_bai_dang, upload_files_chuyen_khoa, upload_files_lam_sang, upload_view, them_moi_thuoc_phong_tai_chinh, create_thuoc, cong_ty, update_lich_hen, danh_sach_lich_hen, store_update_lich_hen, ThanhToanHoaDonThuocToggle, thanh_toan_hoa_don_thuoc, them_thuoc_phong_tai_chinh, upload_view_lam_sang, view_chinh_sua_nhom_quyen, view_danh_sach_nhan_vien, view_danh_sach_nhom_quyen, view_ket_qua_xet_nghiem, xoa_bac_si, xoa_bai_dang, xoa_benh_nhan, xoa_chi_so, xoa_chuoi_kham, xoa_dich_vu, xoa_ket_qua_chuyen_khoa, xoa_lich_hen, xoa_mau_phieu, xoa_nhom_quyen, xoa_phan_khoa_kham, xoa_thuoc, xoa_tieu_chuan, xoa_vat_tu, them_pcn_kem_dich_vu, xoa_lich_hen, xuat_bao_cao_ton, xuat_bao_cao_ton_dich_vu, xuat_bao_hiem, upload_ket_qua_lam_sang, upload_ket_qua_chuyen_khoa

from medicine.views import ke_don_thuoc_view
from clinic.views import create_vat_tu, hoa_don_dich_vu_bao_hiem, hoa_don_thuoc_bao_hiem, loginUser, store_thong_ke_vat_tu, store_update_phong_kham, them_vat_tu, thong_ke_vat_tu, thong_tin_phong_kham, update_phong_kham

router = routers.DefaultRouter()
router.register('api/nguoi_dung', UserViewSet, basename="users")
router.register('api/dich_vu', DichVuKhamViewSet, basename="dich_vu_kham")
router.register('api/phong_chuc_nang', PhongChucNangViewSet, basename="phong_chuc_nang")
router.register('api/lich_kham', LichHenKhamViewSet, basename="lich_kham")
router.register('api/chuoi_kham', ChuoiKhamViewSet, basename="chuoi_kham")
router.register('api/danh_sach_thuoc', ThuocViewSet, basename="thuoc"),
router.register('api/cong_ty', CongTyViewSet, basename="cong_ty")

# ajax_router = routers.DefaultRouter()
# ajax_router.register('', FileKetQuaViewSet, basename="upload")

nguoi_dung = UserViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
    }
)

dich_vu = DichVuKhamViewSet.as_view(
    {   
        'post': 'create',
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }
)

them_thuoc = ThuocViewSet.as_view(
    {
        'post': 'create'
    }
)

phong_chuc_nang = PhongChucNangViewSet.as_view(
    {
        'get': 'retrieve',
        'put': 'update',
        'delete': 'destroy'
    }
)

lich_kham = LichHenKhamViewSet.as_view(
    {
        'get': 'retrieve', 
        'put': 'update', 
        'delete': 'destroy'
    }
)

chuoi_kham = ChuoiKhamViewSet.as_view(
    {
        'get': 'retrieve', 
        'put': 'update', 
        'delete': 'destroy'
    }
)

urlpatterns = [
    path('router/', include(router.urls)),

    # * API
    path('router/api/nguoi_dung/<int:pk>/', nguoi_dung, name='nguoi_dung'),
    path('router/api/dich_vu/<int:pk>/', dich_vu, name='dich_vu'),
    path('router/api/phong_chuc_nang/<int:pk>/', phong_chuc_nang, name='phong_chuc_nang'),

    path('api/dich_vu_kham/', DichVuKhamListCreateAPIView.as_view()),
    path('api/thuoc/', ThuocListCreateAPIView.as_view()),

    path('api/them_thuoc/', create_thuoc, name="them_thuoc_api"),
    # path('api/dieu_phoi/phong_chuc_nang/<int:pk>/', DieuPhoiPhongChucNangView.as_view(), name='dieu_phoi'),
    # path('api/lich_kham<int:pk>/', lich_kham, name='lich_kham'),
    path('api/danh_sach_benh_nhan_cho_lam_sang/', DanhSachBenhNhanChoLamSang.as_view(), name='danh_sach_benh_nhan_cho_lam_sang'),
    path('router/api/chuoi_kham/<int:pk>/', chuoi_kham, name='chuoi_kham'),
    path('api/danh_sach_lich_hen/', ListNguoiDungDangKiKham.as_view(), name='danh_sach_lich_hen'),
    path('api/danh_sach_chuoi_kham/', ChuoiKhamNguoiDung.as_view(), name='danh_sach_chuoi_kham_nguoi_dung'),
    path('api/danh_sach_benh_nhan_theo_phong/', DanhSachBenhNhanTheoPhong.as_view(), name='danh_sach_benh_nhan_theo_phong'),
    path('api/dich_vu_kham/phong_chuc_nang/', PhongChucNangTheoDichVu.as_view(), name='phong_chuc_nang_theo_dich_vu'),
    path('api/thong_tin_phong_chuc_nang/', ThongTinPhongChucNang.as_view(), name='thong_tin_phong_chuc_nang'),
    path('api/danh_sach_phong_chuc_nang/', DanhSachPhongChucNang.as_view(), name='danh_sach_phong_chuc_nang'),
    path('api/danh_sach_dich_vu_theo_phong_chuc_nang/', DanhSachDichVuTheoPhongChucNang.as_view(), name='danh_sach_dich_vu_kham_theo_phong_chuc_nang'),
    path('api/danh_sach_thuoc_theo_cong_ty/', DanhSachThuocTheoCongTy.as_view(), name='danh_sach_thuoc_theo_cong_ty'),
    path('api/danh_sach_dich_vu_kham_theo_phong/', DanhSachDichVuKhamTheoPhong.as_view(), name='danh_sach_dich_vu_kham_theo_phong'),
    path('api/danh_sach_bai_dang/', DanhSachBaiDang.as_view(), name='danh_sach_bai_dang'),
    path('api/ket_qua_chuoi_kham/', KetQuaChuoiKhamBenhNhan.as_view(), name="ket_qua_chuoi_kham"),
    path('api/ket_qua_chuoi_kham_nguoi_dung/', KetQuaChuoiKhamBenhNhan2.as_view(), name="ket_qua_chuoi_kham"),
    path('api/cong_ty/', DanhSachNguonCung.as_view(), name='danh_sach_nguon_cung'),

    # path('upload/', include(ajax_router.urls)),
    path('api/danh_sach_thanh_toan/', DanhSachHoaDonDichVu.as_view(), name='danh_sach_thanh_toan'),
    path('api/danh_sach_hoa_don_thuoc/', DanhSachHoaDonThuoc.as_view(), name='danh_sach_hoa_don_thuoc'),
    path('api/danh_sach_doanh_thu_theo_thoi_gian/', DanhSachDoanhThuTheoThoiGian.as_view(), name='danh_sach_doanh_thu_theo_thoi_gian'),
    path('api/danh_sach_don_thuoc_da_ke/', DanhSachDonThuocDaKe.as_view(), name='danh_sach_don_thuoc_da_ke'),
    path('api/danh_sach_lam_sang/', DanhSachThanhToanLamSang.as_view(), name='danh_sach_lam_sang'),
    path('api/danh_sach_kham_trong_ngay/', DanhSachKhamTrongNgay.as_view(), name='danh_sach_kham_trong_ngay'),
    path('api/thanh_toan_don_thuoc/', ThanhToanHoaDonThuocToggle.as_view(), name='thanh_toan_don_thuoc_api'),
    path('api/danh_sach_don_thuoc_phong_thuoc/', DanhSachDonThuocPhongThuoc.as_view(), name='danh_sach_don_thuoc_phong_thuoc'),
    path('api/thanh_toan_hoa_don_dich_vu/', ThanhToanHoaDonDichVuToggle.as_view(), name='thanh_toan_hoa_don_dich_vu_api'),
    path('api/danh_sach_benh_nhan/', DanhSachBenhNhanListCreateAPIView.as_view(), name='danh_sach_benh_nhan'),
    path('api/danh_sach_benh_nhan_theo_thoi_gian/', DanhSachLichHenTheoBenhNhan.as_view(), name='danh_sach_benh_nhan_theo_thoi_gian'),
    path('api/thong_tin_benh_nhan_theo_ma/', ThongTinBenhNhanTheoMa.as_view(), name='thong_tin_benh_nhan_thao_ma'),
    path('api/danh_sach_phong_chuc_nang/', DanhSachPhongChucNang.as_view(), name='danh_sach_phong_chuc_nang_api'),

    path('api/danh_sach_phan_khoa/', PhanKhoaKhamBenhNhan.as_view(), name='danh_sach_phan_khoa'),
    path('api/benh_nhan/danh_sach_don_thuoc/', DanhSachDonThuocBenhNhan.as_view(), name='danh_sach_don_thuoc_benh_nhan'),
    path('api/benh_nhan/don_thuoc/', DanhSachThuocBenhNhan.as_view(), name='danh_sach_thuoc_benh_nhan'),
    path('api/benh_nhan/tat_ca_lich_hen/', TatCaLichHenBenhNhan.as_view(), name='tat_ca_lich_hen'),
    path('api/benh_nhan/chuoi_kham_gan_nhat/', ChuoiKhamGanNhat.as_view(), name='chuoi_kham_gan_nhat'),
    path('api/benh_nhan/danh_sach_chuoi_kham/', DanhSachChuoiKhamBenhNhan.as_view(), name='danh_sach_chuoi_kham_benh_nhan'),
    path('api/benh_nhan/danh_sach_ket_qua_chuoi_kham/', DanhSachKetQuaChuoiKhamBenhNhan.as_view(), name='danh_sach_ket_qua_chuoi_kham'),
    path('api/benh_nhan/chuoi_kham/ket_qua/', KetQuaChuoiKhamBenhNhan.as_view(), name='ket_qua_chuoi_kham_benh_nhan'),
    path('api/banh_nhan/dang_ki_lich_hen/', DangKiLichHen.as_view(), name='dang_ki_lich_hen'),
    path('api/benh_nhan/thong_tin/', UserInfor.as_view(), name='thong_tin_benh_nhan'),
    path('api/lich_hen_sap_toi/', LichHenKhamSapToi.as_view(), name='lich_hen_sap_toi_benh_nhan'),

    path('api/danh_sach_bac_si/', DanhSachBacSi.as_view(), name='danh_sach_bac_si'),
    # path('api/danh_sach_dich_vu/', PaginatedDichVuKhamListView.as_view(), name='danh_sach_dich_vu'),
    path('api/danh_sach_bai_dang/', DanhSachBaiDang.as_view(), name='danh_sach_bai_dang'),
    path('api/danh_sach_phong_chuc_nang/', DanhSachPhongChucNang.as_view(), name='danh_sach_phong_chuc_nang'),

    path('api/don_thuoc_gan_nhat/', DonThuocGanNhat.as_view(), name='don_thuoc_gan_nhat'),

    path('api/province/', FilterDistrict.as_view()),
    path('api/district/', FilterWard.as_view()),
    path('api/benh_nhan/ket_qua_xet_nghiem/', KetQuaXetNghiemMobile.as_view()),
    path('api/benh_nhan/phieu_ket_qua/', PhieuKetQuaMobile.as_view()),

    path('api/funcroom_info/', GetFuncroomInfo.as_view()),

    path('api/danh_sach_benh_nhan_theo_phong_chuc_nang/', DanhSachBenhNhanTheoPhongChucNang.as_view(), name="danh_sach_benh_nhan_theo_phong_chuc_nang"),
    path('api/bat_dau_chuoi_kham/', BatDauChuoiKhamToggle.as_view(), name='bat_dau_chuoi_kham_api'),
    path('api/ket_thuc_chuoi_kham/', KetThucChuoiKhamToggle.as_view(), name='ket_thuc_chuoi_kham_api'),
    path('api/danh_sach_doanh_thu_dich_vu/', DanhSachDoanhThuDichVu.as_view(), name='danh_sach_doanh_thu_dich_vu'),
    path('api/danh_sach_doanh_thu_thuoc/', DanhSachDoanhThuThuoc.as_view(), name='danh_sach_daonh_thu_thuoc'),
    
    path('api/thong_tin_phong_kham/', ThongTinPhongKham.as_view(), name='thong_tin_phong_kham'),
    
    # * VIEW
    path('', RedirectView.as_view(url='trang_chu/'), name='index'),
    path('trang_chu/', index, name='index'),
    path('danh_sach_benh_nhan/', danh_sach_benh_nhan, name='danh_sach_benh_nhan'),
    path('danh_sach_benh_nhan/<int:id>/cap_nhat_thong_tin_benh_nhan', update_benh_nhan, name="update_benh_nhan"),
    path('cap_nhat_thong_tin_benh_nhan/', cap_nhat_thong_tin_benh_nhan, name="cap_nhat_thong_tin_benh_nhan"),
    
    path('bac_si_lam_sang/danh_sach_benh_nhan_cho/', danh_sach_benh_nhan_cho, name='danh_sach_benh_nhan_cho'),
    path('dang_nhap/', LoginView.as_view(), name='dang_nhap'),
    path('dang_ki/', create_user, name="dang_ki_nguoi_dung"),
    path('phong_chuyen_khoa/<int:id_phong_chuc_nang>/', phong_chuyen_khoa, name='phong_chuyen_khoa'),
    path('phong_chuyen_khoa/<int:id_dich_vu>/benh_nhan/<int:id>/upload/<int:id_phan_khoa>/', view_ket_qua_xet_nghiem, name='upload_ket_qua_chuyen_khoa_view'),
    path('danh_sach_benh_nhan_cho/phan_khoa_kham/<int:id_lich_hen>/', phan_khoa_kham, name='phan_khoa_kham'),
    path('bac_si_lam_sang/ket_qua_kham/', danh_sach_kham, name='danh_sach_kham'),
    path('bac_si_lam_sang/benh_nhan/<int:id>/upload/', upload_view_lam_sang, name='upload_ket_qua_lam_sang_view'),
    path('danh_sach_kham/ke_don_thuoc/<int:user_id>/<int:id_chuoi_kham>/', ke_don_thuoc_view, name='ke_don_thuoc'),

    # path('test/', testView, name="test"),
    path('store_phan_khoa_kham/', store_phan_khoa, name='store_phan_khoa'),
    path('store_ke_don/', store_ke_don, name='store_ke_don'),
    path('chinh_sua_ke_don/', chinh_sua_don_thuoc, name='chinh_sua_don_thuoc'),
    path('ke_don_thuoc/', ke_don_thuoc_view, name='ke_don_thuoc'),
    path('upload_files/', files_upload_view, name='upload_files'),

    # path('upload/<int:id>/', upload_view, name='upload'),
    path('upload_files_chuyen_khoa/', upload_files_chuyen_khoa, name="upload_files_chuyen_khoa"),
    path('upload_files_lam_sang/', upload_files_lam_sang, name='upload_files_lam_sang'),
    path('store_cong_ty/', store_cong_ty, name='store_cong_ty'),

    path('danh_sach_lich_hen/', danh_sach_lich_hen, name='danh_sach_lich_hen'),
    path('danh_sach_lich_hen/lich_hen/<int:id>/', update_lich_hen, name='update_lich_hen'),
    path('store_update_lich_hen', store_update_lich_hen, name="store_update_lich_hen"),
    path('xoa_lich_hen/', xoa_lich_hen, name="xoa_lich_hen"),
    path('set_cho_thanh_toan/', SetChoThanhToan.as_view(), name="set_cho_thanh_toan"),
    path('set_xac_nhan_kham/', SetXacNhanKham.as_view(), name="set_xac_nhan_kham"),

    path('bat_dau_chuoi_kham/<int:id>/', bat_dau_chuoi_kham, name='bat_dau_chuoi_kham'),
    path('bac_si_lam_sang/dung_kham_dot_xuat/', dung_kham, name='dung_kham'),
    # path('bac_si_lam_sang/dung_kham_ket_qua_chuyen_khoa', dung_kham_ket_qua_chuyen_khoa, name="dung_kham_ket_qua_chuyen_khoa"),
    path('bac_si_lam_sang/dung_kham_ket_qua_chuyen_khoa/', dung_kham_ket_qua_chuyen_khoa, name='dung_kham_ket_qua_chuyen_khoa'),
    path('bac_si_chuyen_khoa/dung_kham/', dung_kham_chuyen_khoa, name='dung_kham_chuyen_khoa'),

# ---- MINH UPdate -----
# * -------------------- Update -----------------------
    path('api/thong_tin_chinh_sua/', UserUpdateInfo.as_view(), name='thong_tin_chinh_sua'),
    path('api/chinh_sua_thong_tin/', UserUpdateInfoRequest.as_view(), name='chinh_sua_thong_tin'),
    path('api/chinh_sua_avatar/', UploadAvatarView.as_view(), name='chinh_sua_avatar'),
    path('api/thong_tin_lich_hen/', UpdateAppointmentDetail.as_view(), name='thong_tin_lich_hen'), 
    path('api/chinh_sua_lich_hen/', CapNhatLichHen.as_view(), name='chinh_sua_lich_hen'),
    path('api/hoa_don_chuoi_kham_can_thanh_toan/', HoaDonChuoiKhamCanThanhToan.as_view(), name='hoa_don_chuoi_kham_can_thanh_toan'), 
    path('api/hoa_don_thuoc_can_thanh_toan/', HoaDonThuocCanThanhToan.as_view(), name='hoa_don_thuoc_can_thanh_toan'),

# * update them 
    path('api/danh_sach_dich_vu/phong_chuc_nang/', DichVuTheoPhongChucNang.as_view(), name='phong_chuc_nang_dich_vu'),

#* update 25-12
    path('api/don_thuoc/chuoi_kham/', DonThuocCuaChuoiKham.as_view(), name='don_thuoc_cua_chuoi_kham'),
    path('api/hoa_don_dich_vu/chuoi_kham/', HoaDonDichVuCuaChuoiKham.as_view(), name='hoa_don_dich_vu_cua_chuoi_kham'),
    path('api/hoa_don_thuoc/chuoi_kham/', HoaDonThuocCuaChuoiKham.as_view(), name='hoa_don_thuoc_cua_chuoi_kham'),
    path('api/hoa_don_lam_sang/', HoaDonLamSangChuoiKham.as_view(), name='hoa_don_lam_sang'),
    path('api/hoa_don_lam_sang_gan_nhat/', HoaDonLamSangGanNhat.as_view(), name='hoa_don_lam_sang_gan_nhat'),

    path('api/get_so_phieu_cls/', FilterBaoHiem.as_view(), name='get_so_phieu_cls'),
    path('store_ket_qua_xet_nghiem/', store_ket_qua_xet_nghiem, name='store_ket_qua_xet_nghiem'),

    path('them_mau_phieu/', them_mau_phieu, name='them_mau_phieu'),
    path('mau_phieu/<int:id>/', chi_tiet_mau_phieu, name='chi_tiet_mau_phieu'),
    path('create_mau_phieu/', create_mau_phieu, name='create_mau_phieu'),
    path('update_mau_phieu/', update_mau_phieu, name='update_mau_phieu'),
    path('danh_sach_mau_phieu/', danh_sach_mau_phieu, name='danh_sach_mau_phieu'),
    path('api/danh_sach_mau_phieu/', DanhSachMauPhieu.as_view(), name='api_danh_sach_mau_phieu'),
    path('test_mau_phieu/', test_mau_phieu),

    path('dang_ki_tieu_chuan/', dang_ki_tieu_chuan_view, name='dang_ki_tieu_chuan_view'),
    path('create_tieu_chuan/', create_tieu_chuan, name='create_tieu_chuan'),
    path('xoa_tieu_chuan/', xoa_tieu_chuan, name='xoa_tieu_chuan'),
    path('xoa_chi_so/', xoa_chi_so, name='xoa_chi_so'),

    path('chi_tiet_tieu_chuan/<int:id>/', chi_tiet_tieu_chuan_dich_vu, name='chi_tiet_tieu_chuan'),
    path('danh_sach_tieu_chuan/', list_tieu_chuan_dich_vu, name='list_tieu_chuan_dich_vu'),
    path('api/danh_sach_tieu_chuan/', ListTieuChuanDichVu.as_view()),
    path('chinh_sua_tieu_chuan/', chinh_sua_tieu_chuan_dich_vu, name='chinh_sua_tieu_chuan_dich_vu'),

    path('export_excel/', export_excel, name='export_excel'),
    path('export_dich_vu_bao_hiem_excel/', export_dich_vu_bao_hiem_excel, name='export_dich_vu_excel'),
    path('export_thuoc_bao_hiem_excel/', export_thuoc_bao_hiem_excel, name='export_thuoc_excel'),

    path('api/benh_nhan_huong_bao_hiem/export/', ApiExportBenhNhanBaoHiemExcel.as_view()),
    path('api/dich_vu_ky_thuat/export/', ApiExportExcelDichVu.as_view()),
    path('api/thuoc/export/', ApiExportExcelThuoc.as_view()),

    path('api/benh_nhan/lich_hen/', TatCaLichHenBenhNhanList.as_view(), name='api_tat_ca_lich_hen_benh_nhan'),
    path('api/tim_kiem/', TimKiemKetQuaBenhNhan.as_view(), name="tim_kiem_ket_qua_benh_nhan"),
    path('benh_nhan/<int:id>/tat_ca_lich_hen/', tat_ca_lich_hen_banh_nhan, name='tat_ca_lich_hen_benh_nhan'),
    path('benh_nhan/lich_hen/<int:id>/', chi_tiet_lich_hen_benh_nhan, name='chi_tiet_lich_hen_benh_nhan'),
    path('benh_nhan/ket_qua_chuyen_khoa/<int:id>/', chi_tiet_ket_qua_xet_nghiem, name='chi_tiet_ket_qua_xet_nghiem'),
    path('benh_nhan/phieu_ket_qua/<int:id>/', chi_tiet_phieu_ket_qua, name='chi_tiet_phieu_ket_qua'),
    path('benh_nhan/phieu_ket_qua_tong_quat/<int:id>/', chi_tiet_phieu_ket_qua_lam_sang, name='chi_tiet_phieu_ket_qua_tong_quat'),
    path('phieu_ket_qua/<int:id>/', phieu_ket_qua, name='phieu_ket_qua'),
    path('phieu_ket_qua_lam_sang/<int:id>/', phieu_ket_qua_tong_quat, name='phieu_ket_qua_lam_sang'),

    path('xoa_benh_nhan/', xoa_benh_nhan, name='xoa_benh_nhan'),
    path('dat_lai_mat_khau/', resetPassword, name='dat_lai_mat_khau'),
    path('cap_nhat_mat_khau/', changePassword, name='change_password'),
    path('xoa_mau_phieu/', xoa_mau_phieu, name='xoa_mau_phieu'),
    path('xoa_bai_dang/', xoa_bai_dang, name='xoa_bai_dang'),
    path('chinh_sua/bai_dang/<int:id>/', chinh_sua_bai_dang_view, name='chinh_sua_bai_dang'),
    path('cap_nhat_bai_dang/', chinh_sua_bai_dang, name="cap_nhat_bai_dang"),

    path('ket_qua_benh_nhan/', ket_qua_benh_nhan_view, name='ket_qua_benh_nhan'),
    path('ket_qua_benh_nhan/chuoi_kham/<int:id_chuoi_kham>/', chi_tiet_chuoi_kham_benh_nhan, name='chi_tiet_chuoi_kham_benh_nhan'),
    path('api/don_thuoc/', XemDonThuoc.as_view()),
    path('store_phieu_ket_qua/', store_ket_qua_chuyen_khoa_html, name='store_ket_qua_chuyen_khoa_html'),


    path('phong_tai_chinh/', phong_tai_chinh_danh_sach_cho, name='phong_tai_chinh'),
    path('phong_thuoc/', phong_thuoc_danh_sach_cho, name='phong_thuoc'),
    path('phong_tai_chinh/hoa_don_dich_vu/<int:id_chuoi_kham>/', hoa_don_dich_vu, name='hoa_don_dich_vu'),
    path('phong_tai_chinh/hoa_don_thuoc/<int:id_don_thuoc>/', hoa_don_thuoc, name='hoa_don_thuoc'),
    path('phong_tai_chinh/danh_sach_thuoc/', danh_sach_thuoc_phong_tai_chinh, name='danh_sach_thuoc_phong_tai_chinh'),
    path('phong_tai_chinh/hoa_don_thuoc/thanh_toan/', thanh_toan_hoa_don_thuoc, name='thanh_toan_hoa_don_thuoc'),
    path('phong_tai_chinh/them_thuoc/', them_thuoc_phong_tai_chinh, name='them_thuoc_phong_tai_chinh'),
    path('phong_thuoc/don_thuoc/<int:id_don_thuoc>/', don_thuoc, name='don_thuoc'),
    path('phong_thuoc/danh_sach_thuoc/', danh_sach_thuoc, name='danh_sach_thuoc_phong_thuoc'),
    path('phong_tai_chinh/them_moi_thuoc/', them_moi_thuoc_phong_tai_chinh, name="phong_tai_chinh_them_moi_thuoc"),
    path('phong_tai_chinh/danh_sach_vat_tu/', danh_sach_vat_tu, name='danh_sach_vat_tu'),
    path('phong_tai_chinh/them_vat_tu_excel/', them_vat_tu_excel, name='them_vat_tu_excel'),
    path('store_vat_tu_excel/', import_vat_tu_excel, name="import_vat_tu_excel"),
    path('store_dich_vu_kham/', create_dich_vu, name="store_dich_vu_kham"),
    path('nguon_cung/', cong_ty, name="nguon_cung"),
    path('nguon_cung/<int:id>/chinh_sua/', update_nguon_cung, name="update_nguon_cung"),
    path('chinh_sua/', chinh_sua_nguon_cung, name="chinh_sua"),
    path('danh_sach_phong_chuc_nang/', danh_sach_phong_chuc_nang, name="danh_sach_phong_chuc_nang"),
    path('them_phong_chuc_nang/', them_phong_chuc_nang, name="them_phong_chuc_nang"),
    path('danh_sach_dich_vu_kham/', danh_sach_dich_vu_kham, name="danh_sach_dich_vu_kham"),
    # path('danh_sach_phong_chuc_nang/<int:id>/chinh_sua_phong_chuc_nang', update_phong_chuc_nang, name="update_phong_chuc_nang"),
    path('danh_sach_dich_vu_kham/<int:id>/chinh_sua_dich_vu_kham', update_dich_vu_kham, name="update_dich_vu_kham"),
    path('chinh_sua_phong_chuc_nang/', chinh_sua_phong_chuc_nang, name="chinh_sua_phong_chuc_nang"),
    path('cap_nhat_thong_tin/<int:id>', update_user, name="update_user"),
    path('cap_nhat_user/', cap_nhat_user, name="cap_nhat_user"),
    path('phong_tai_chinh/danh_sach_thuoc/<str:id_thuoc>/cap_nhat_thuoc/', chinh_sua_thuoc, name="cap_nhat_thuoc"),
    path('update_thuoc/', update_thuoc, name="update_thuoc"),
    path('phong_thuoc/danh_sach_thuoc/<str:id_thuoc>/cap_nhat_thuoc/', chinh_sua_thuoc_phong_thuoc, name="cap_nhat_thuoc_phong_thuoc"),
    path('update_thuoc_phong_thuoc/', update_thuoc_phong_thuoc, name="update_thuoc_phong_thuoc"),
    path('phong_tai_chinh/doanh_thu_phong_kham/', doanh_thu_phong_kham, name="doanh_thu_phong_kham"),
    path('them_dich_vu_kham_excel/', them_dich_vu_kham_excel, name='them_dich_vu_kham_excel'),
    # path('store_dich_vu_excel/', import_dich_vu_excel, name="import_dich_vu_excel"),
    path('them_thuoc_excel/', them_thuoc_excel, name="them_thuoc_excel"),
    path('import_thuoc_excel/', import_thuoc_excel, name="import_thuoc_excel"),
    path('them_dich_vu_kham/', them_dich_vu_kham, name="them_dich_vu_kham"),
    path('tao_lich_hen/', add_lich_hen, name='add_lich_hen'),
    path('danh_sach_bai_dang/', danh_sach_bai_dang, name="danh_sach_bai_dang"),
    path('thanh_toan_lam_sang/', store_thanh_toan_lam_sang, name="store_thanh_toan_lam_sang"),
    path('don_thuoc/chinh_sua/<int:id>/', update_don_thuoc, name="update_don_thuoc"),
    path('nhan_don_thuoc/', nhan_don_thuoc, name="nhan_don_thuoc"),

    # * update -- 22/01 --
    path('them_benh_excel/', them_ma_benh_excel, name="them_benh_excel"),
    path('import_benh_excel/', import_ma_benh_excel, name="import_ma_benh_excel"),
 
    path('them_pcn/_kem_dich_vu/', them_pcn_kem_dich_vu, name='them_pcn_kem_dich_vu'),
    path('them_bai_dang/', them_bai_dang, name="them_bai_dang"),
    path('upload_bai_dang/', upload_bai_dang, name="upload_bai_dang"),
    path('bai_dang/<int:id>/', chi_tiet_bai_dang, name="chi_tiet_bai_dang"),
    
    path('xoa_thuoc/', xoa_thuoc, name="xoa_thuoc"),
    path('xoa_dich_vu/', xoa_dich_vu, name="xoa_dich_vu"),
    path('xoa_chuoi_kham/', xoa_chuoi_kham, name='xoa_chuoi_kham'),
    path('store_update_dich_vu_kham/', store_update_dich_vu_kham, name="store_update_dich_vu_kham"),
    path('api/danh_sach_vat_tu/', DanhSachVatTu.as_view(), name="api_danh_sach_vat_tu"),
    path('xoa_vat_tu/', xoa_vat_tu, name="xoa_vat_tu"),
    

    path('login/', login, name='login'),
    path('loginUser/', loginUser, name='loginUser'),
    # path('logout/',auth_views.LogoutView.as_view(next_page='dang_nhap'),name='logout'),
    path('logout/', logout_view, name='logout_view'),
    
    # UPDATE BY LONG
    path('danh_sach_bac_si/', danh_sach_bac_si, name="view_danh_sach_bac_si"),
    path('create_bac_si/', create_bac_si, name="create_bac_si"),
    path('api/danh_sach_bac_si_api/', DanhSachBacSi1.as_view(), name="danh_sach_bac_si_api"),
    path('danh_sach_bac_si/<int:id>/<int:user_id>/cap_nhat_thong_tin/', update_bac_si, name="update_bac_si"),
    path('cap_nhat_thong_tin_bac_si/', cap_nhat_thong_tin_bac_si, name="cap_nhat_thong_tin_bac_si"),
    # END
    
    # UPDATE NGAY 3/1
    path('xoa_lich_hen/', xoa_lich_hen, name="xoa_lich_hen"), 
    path('phong_tai_chinh/xuat_bao_hiem/', xuat_bao_hiem, name="xuat_bao_hiem"), 
    path('phong_tai_chinh/danh_sach_benh_nhan_huong_bao_hiem/', danh_sach_benh_nhan_bao_hiem, name='danh_sach_benh_nhan_bao_hiem'),
    path('phong_tai_chinh/danh_sach_dich_vu_ky_thuat_bao_hiem/', danh_sach_dich_vu_bao_hiem, name='danh_sach_dich_vu_bao_hiem'),
    path('phong_tai_chinh/danh_sach_thuoc_bao_hiem/', danh_sach_thuoc_bao_hiem, name='danh_sach_thuoc_bao_hiem'),

    path('api/danh_sach_hoa_don_dich_vu_bao_hiem/', DanhSachHoaDonDichVuBaoHiem.as_view(), name="danh_sach_hoa_don_dich_vu_bao_hiem"),
    path('upload_ket_qua_lam_sang/', upload_ket_qua_lam_sang, name="upload_ket_qua_lam_sang"),
    path('upload_ket_qua_chuyen_khoa/', upload_ket_qua_chuyen_khoa, name="upload_ket_qua_chuyen_khoa"),
    path('api/danh_sach_doanh_thu_lam_sang/', DanhSachDoanhThuLamSang.as_view(), name="danh_sach_doanh_thu_lam_sang"), #import DoanhThuLamSang
    path('api/danh_sach_doanh_thu_theo_phong_chuc_nang/', DoanhThuTheoPhongChucNang.as_view(), name='danh_sach_doanh_thu_theo_phong_chuc_nang'),

    # END

    # UPDATE 9/1
    path('thong_tin_phong_kham/', thong_tin_phong_kham, name="thong_tin_phong_kham"),
    path('thong_ke_vat_tu/', thong_ke_vat_tu, name="thong_ke_vat_tu"),
    path('store_thong_ke_vat_tu/', store_thong_ke_vat_tu, name="store_thong_ke_vat_tu"),
    path('phong_tai_chinh/them_vat_tu/', them_vat_tu, name="them_vat_tu"),
    path('create_vat_tu/', create_vat_tu, name="create_vat_tu"),
    path('api/danh_sach_phong_kham/', DanhSachPhongKham.as_view(), name="danh_sach_phong_kham_api"),
    path('cap_nhat_thong_tin_phong_kham/<int:id>', update_phong_kham, name="update_phong_kham"),
    path('store_update_phong_kham/', store_update_phong_kham, name="store_update_phong_kham"),
    path('api/danh_sach_hoa_don_thuoc_bao_hiem/', DanhSachHoaDonThuocBaoHiem.as_view(), name="danh_sach_hoa_don_thuoc_bao_hiem_api"),
    path('xuat_bao_hiem/dich_vu/<int:id>', hoa_don_dich_vu_bao_hiem, name="hoa_don_dich_vu_bao_hiem"),
    path('xuat_bao_hiem/thuoc/<int:id>', hoa_don_thuoc_bao_hiem, name="hoa_don_thuoc_bao_hiem"),
    # END

    # update 13/1
    path("create_user_index/", create_user_index, name="create_user_index"),
    path("phong_tai_chinh/danh_sach_vat_tu/<int:id>/chinh_sua", update_vat_tu, name="update_vat_tu"),
    path("update_vat_tu/", store_update_vat_tu, name="store_update_vat_tu"),

    # UPDATE BY LONG
    path("xoa_bac_si/", xoa_bac_si, name="xoa_bac_si"),
    path('create_lich_tai_kham/', create_lich_tai_kham, name="create_lich_tai_kham"),
    path('phong_thuoc/tao_don_thuoc/', create_don_thuoc_rieng, name="create_don_thuoc_rieng"),
    path('store_don_thuoc_rieng/', store_don_thuoc_rieng, name="store_don_thuoc_rieng"),
    path('api/danh_sach_lich_su_kham_benh_nhan/', DanhSachLichSuKhamBenhNhan.as_view(), name="danh_sach_lich_su_kham_benh_nhan"),

    # superuser section (update 23/03/2021)
    path('danh_sach_nhom_quyen/', view_danh_sach_nhom_quyen, name='danh_sach_nhom_quyen'),
    path('danh_sach_nhan_vien/', view_danh_sach_nhan_vien, name='danh_sach_nhan_vien'),
    path('create_staff_user/', create_staff_user, name='create_staff_user'),
    path('store_nhom_quyen/', store_nhom_quyen, name='store_nhom_quyen'),
    path('store_uy_quyen/', store_uy_quyen, name='store_uy_quyen'),
    path('nhom_quyen/<int:id>/chinh_sua/', view_chinh_sua_nhom_quyen, name='chinh_sua_nhom_quyen'),
    path('update_nhom_quyen/', update_nhom_quyen, name="update_nhom_quyen"),
    path('api/danh_sach_nhom_quyen/', ApiListGroup.as_view()),
    path('api/danh_sach_nhan_vien/', ApiListStaff.as_view()),
    path('api/nhom_quyen/nguoi_dung/', ApiListAllGroupOfUser.as_view()),

    # UPDATE LONG 27/3
    path('update_nhan_vien/<int:id>', update_nhan_vien, name="update_nhan_vien"),
    path('cap_nhat_thong_tin_nhan_vien/', cap_nhat_thong_tin_nhan_vien, name="cap_nhat_thong_tin_nhan_vien"),

    path('dich_vu_ky_thuat/import/', import_dich_vu_kham_view, name='import_dich_vu_ky_thuat'),
    path('thuoc/import/', import_thuoc_view, name="import_thuoc"),
    path('store_dich_vu_excel/', store_dich_vu_kham_excel, name='store_dich_vu_excel'),
    path('store_thuoc_excel/', store_thuoc_excel, name='store_thuoc_excel'),
    path('store_thuoc_dich_vu_excel/', store_thuoc_dich_vu_excel, name='store_thuoc_dich_vu_excel'),
    path('nhap_them_thuoc/', nhap_them_thuoc, name="nhap_them_thuoc"),

    path('lich_su_hoat_dong/', my_activities, name='my_activities'),

    path('xoa_nhom_quyen/', xoa_nhom_quyen, name='xoa_nhom_quyen'),
    path('store_nhap_hang/', store_nhap_thuoc, name="store_nhap_thuoc"),
    path('bao_cao_thuoc/', bao_cao_thuoc, name="bao_cao_thuoc"),
    path('api/danh_sach_bao_cao_theo_thoi_gian/', DanhSachBaoCaoTheoThoiGian.as_view(), name='danh_sach_bao_cao_theo_thoi_gian'),
    path('api/danh_sach_nhung_thuoc_duoc_nhap/', DanhSachNhungThuocDuocNhap.as_view(), name='danh_sach_nhung_thuoc_duoc_nhap'),
    path('xuat_bao_cao_ton/', xuat_bao_cao_ton, name="xuat_bao_cao_ton"),
    path('xuat_bao_cao_ton_dich_vu/', xuat_bao_cao_ton_dich_vu, name='xuat_bao_cao_ton_dich_vu'),
    path('api/danh_sach_nhung_thuoc_duoc_xuat/', DanhSachNhungThuocDuocXuat.as_view(), name="danh_sach_nhung_thuoc_duoc_xuat"),
    path('phong_tai_chinh/hoa_don_tpcn/<int:id_don_thuoc>/', hoa_don_tpcn, name='hoa_don_tpcn'),
    path('api/danh_sach_thuoc_dich_vu_nhap/', DanhSachThuocNhapDichVu.as_view()),
    path('api/danh_sach_thuoc_dich_vu_xuat/', DanhSachThuocXuatDichVu.as_view()),

    path('api/check_exists_so_dien_thoai/', check_so_dien_thoai_exists, name='check_exists_so_dien_thoai'),
    path('api/check_exists_username/', check_username_exists, name='check_exists_username'),

    path('them_mau_hoa_don/', them_mau_hoa_don, name='them_mau_hoa_don'),
    path('create_mau_hoa_don/', create_mau_hoa_don, name='create_mau_hoa_don'),
    path('update_mau_hoa_don/', update_mau_hoa_don, name='update_mau_hoa_don'),

    path('api/danh_sach_phan_khoa/chuoi_kham/', GetDanhSachPhanKhoaCuaChuoiKham.as_view(), name='danh_sach_phan_khoa_chuoi_kham'),
    path('thay_doi_phan_khoa/', thay_doi_phan_khoa, name='thay_doi_phan_khoa'),
    path('thay_doi_phan_khoa_hoa_don_dich_vu/', thay_doi_phan_khoa_hoa_don_dich_vu, name='thay_doi_phan_khoa_hoa_don_dich_vu'),
    path('api/danh_sach_benh_nhan_da_kham/', XemLaiBenhNhanDaKhamChuyenKhoaAPIView.as_view()),
    path('api/danh_sach_benh_nhan_da_kham_lam_sang/', XemLaiBenhNhanLamSangAPIView.as_view()),

    path('hoa_don_lam_sang/<int:id>/', hoa_don_lam_sang, name='xem_lai_hoa_don_lam_sang'),
    # END UPDATE

    path('api/xuat_nhap_tong_thuoc_tong_hop/', XuatNhapTongThuocAPIView.as_view()),
    path('export_excel/xuat_nhap_ton_thuoc_tong_hop/', export_excel_danh_sach_xnt_tong_hop_thuoc, name='export_excel_danh_sach_xnt_tong_hop_thuoc'),
    path('api/danh_sach_thuoc_sap_het_han/', DanhSachThuocSapHetHan.as_view()),
    path('export_excel/danh_sach_thuoc_sap_het_date/', export_excel_danh_sach_thuoc_het_date, name='export_excel_danh_sach_thuoc_het_date'),

    path('bao_cao_xnt_tong_hop_thuoc/', bao_cao_xuat_nhap_ton_thuoc_view, name='bao_cao_xnt_tong_hop_thuoc'),
    path('bao_cao_thuoc_sap_het_date/', danh_sach_thuoc_sap_het_date_view, name='bao_cao_thuoc_sap_het_date'),
    path('api/chi_tiet_mau_phieu/', ChiTietMauPhieuAPIView.as_view()),
    path('hoan_thanh_kham/', hoan_thanh_kham, name='hoan_thanh_kham'),
    path('hoan_thanh_kham_dich_vu/', hoan_thanh_kham_hoa_don, name='hoan_thanh_kham_hoa_don'),
    path('api/set_dich_vu_html/', SetHtmlDichVuKham.as_view()),
    path('api/set_dich_vu_chi_so/', SetChiSoDichVuKham.as_view()),
    path('hoan_thanh_kham_don_thuoc/', hoan_thanh_chuoi_kham_hoa_don_thuoc, name='hoan_thanh_kham_don_thuoc'),
    path('xoa_ket_qua_chuyen_khoa/', xoa_ket_qua_chuyen_khoa, name='xoa_ket_qua_chuyen_khoa'),
    path('api/danh_sach_tieu_chuan_theo_nhom/', DanhSachTieuChuanTheoNhomAPIview.as_view()),
    
    path('tong_hop/', menu_view, name='menu'),
    path('xoa_chi_dinh/', xoa_phan_khoa_kham, name='xoa_chi_dinh'),
    path('chinh_sua_ket_qua/phieu_ket_qua/<int:id_phan_khoa>/', chinh_sua_phieu_ket_qua_view, name='chinh_sua_phieu_ket_qua'),
    path('store_update_phieu_ket_qua/', store_update_phieu_ket_qua, name='store_update_phieu_ket_qua'),

]
