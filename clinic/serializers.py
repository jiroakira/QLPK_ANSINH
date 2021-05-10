from finance.models import HoaDonChuoiKham, HoaDonNhapHang, HoaDonThuoc, HoaDonLamSang, NhapHang
from medicine.serializers import CongTySerializer, ThuocSerializer, ThuocSerializerSimple
# from finance.serializers import HoaDonChuoiKhamSerializer, HoaDonThuocSerializer
from django.http.request import validate_host
from rest_framework import fields, serializers
from django.contrib.auth import get_user_model
from .models import (
    BaiDang, ChiSoXetNghiem, ChiTietChiSoXetNghiem, 
    DichVuKham, District, 
    FileKetQua, 
    FileKetQuaChuyenKhoa, 
    FileKetQuaTongQuat, HtmlKetQua, 
    KetQuaChuyenKhoa, 
    KetQuaTongQuat, KetQuaXetNghiem, 
    LichHenKham, MauPhieu, NhomChiSoXetNghiem, 
    PhanKhoaKham, 
    PhongChucNang, 
    PhongKham, 
    ProfilePhongChucNang, 
    TrangThaiChuoiKham, 
    TrangThaiKhoaKham, 
    TrangThaiLichHen, 
    ChuoiKham, 
    BacSi,
    TinhTrangPhongKham, Ward, send_func_room_info,
)
from medicine.models import DonThuoc, KeDonThuoc, NhomVatTu, TrangThaiDonThuoc, VatTu
from django.contrib.auth.models import Group, Permission

User = get_user_model()

class ChildUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('id', 'so_dien_thoai', 'ho_ten', 'email', 'cmnd_cccd', 'chuc_nang') 

class UserSerializer(serializers.ModelSerializer):
    gioi_tinh = serializers.CharField(source='get_gioi_tinh')
    dia_chi = serializers.CharField(source='get_dia_chi')
    class Meta:
        model = User
        # fields = '__all__'
        fields = ('id', 'so_dien_thoai', 'ho_ten', 'email', 'cmnd_cccd', 'dia_chi', 'ngay_sinh', 'gioi_tinh', 'ma_benh_nhan', 'dan_toc', 'anh_dai_dien', 'ma_so_bao_hiem')
        extra_kwargs = {'password': {'write_only': True}}

    # TODO create and update child instance of user
    # TODO review again

class UserLoginSerializer(serializers.Serializer):
    so_dien_thoai = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class DangKiSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('so_dien_thoai', 'password', 'ho_ten', 'cmnd_cccd', 'dia_chi')
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def create(self, validated_data):
        user = User.objects.create_user(
            ho_ten = validated_data['ho_ten'], 
            so_dien_thoai = validated_data['so_dien_thoai'], 
            password = validated_data['password'],
            cmnd_cccd = validated_data['cmnd_cccd'], 
            dia_chi = validated_data['dia_chi']
        )
        return user

class DichVuKhamSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = DichVuKham
        fields = ('id', 'ma_dvkt', 'ten_dvkt', 'ma_gia', 'quyet_dinh', 'cong_bo', 'ma_cosokcb')

class TrangThaiLichHenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrangThaiLichHen
        fields = '__all__'

    # def create(self, validated_data):
    #     ten_dich_vu = validated_data.get('ten_dich_vu')
    #     dich_vu = DichVuKham.objects.get_or_create(ten_dich_vu = ten_dich_vu)[0]
    #     return dich_vu

    # def to_representation(self, instance):
    #     response = super().to_representation(instance)
    #     response['bac_si_phu_trach'] = UserSerializer(instance.bac_si_phu_trach).data
    #     return response

class PhongChucNangSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhongChucNang
        fields = '__all__'

    def create(self, validated_data):
        ten_phong_chuc_nang = validated_data.get('ten_phong_chuc_nang')
        phong_chuc_nang = PhongChucNang.objects.get_or_create(ten_phong_chuc_nang = ten_phong_chuc_nang)[0]
        return phong_chuc_nang

    def to_representation(self, instance):

        response = super().to_representation(instance)
        response['dich_vu_kham'] = DichVuKhamSerializer(instance.dich_vu_kham).data
        return response

class ProfilePhongChucNangSerializer(serializers.ModelSerializer):
    phong_chuc_nang = PhongChucNangSerializer()
    class Meta:
        model = ProfilePhongChucNang
        fields = '__all__'

class TrangThaiLichHenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrangThaiLichHen
        fields = '__all__'


class LichHenKhamSerializer(serializers.ModelSerializer):
    benh_nhan = UserSerializer()
    nguoi_phu_trach = UserSerializer()
    trang_thai = TrangThaiLichHenSerializer()
    trang_thai_thanh_toan = serializers.CharField(source='check_thanh_toan')
    hoan_thanh_kham = serializers.BooleanField(source='check_thanh_toan')
    class Meta:
        model = LichHenKham
        fields = (
            'id',
            'benh_nhan',
            'nguoi_phu_trach',
            'trang_thai',
            'ma_lich_hen',
            'thoi_gian_bat_dau',
            'thoi_gian_ket_thuc',
            'ly_do',
            'dia_diem',
            'loai_dich_vu',
            'ly_do_vvien',
            'thoi_gian_tao',
            'thoi_gian_chinh_sua',
            'trang_thai_thanh_toan',
            'thanh_toan_sau',
            'hoan_thanh_kham',
        )

    def create(self, validated_data):
        benh_nhan = validated_data.get('benh_nhan')
        ngay_hen = validated_data.get('ngay_hen')
        thoi_gian_bat_dau = validated_data.get('thoi_gian_bat_dau')
        lich_hen = LichHenKham.objects.get_or_create(
            benh_nhan=benh_nhan,
            ngay_hen=ngay_hen,
            thoi_gian_bat_dau=thoi_gian_bat_dau
        )
        return lich_hen
    

class TrangThaiLichHenSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrangThaiLichHen
        fields = '__all__'

class TrangThaiKhoaKhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrangThaiKhoaKham
        fields = '__all__'

class TrangThaiChuoiKhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrangThaiChuoiKham
        fields = '__all__'


class ChuoiKhamSerializerSimple(serializers.ModelSerializer):
    benh_nhan = UserSerializer()
    bac_si_dam_nhan = UserSerializer()
    trang_thai = TrangThaiChuoiKhamSerializer()
    hoan_thanh_kham = serializers.CharField(source='lich_hen.check_hoan_thanh_kham')
    class Meta:
        model = ChuoiKham
        fields = ('id', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'benh_nhan', 'bac_si_dam_nhan', 'trang_thai', 'hoan_thanh_kham')

class ChuoiKhamPhanKhoaSerializer(serializers.ModelSerializer):
    trang_thai = TrangThaiChuoiKhamSerializer()
    class Meta:
        model = ChuoiKham
        fields = ('id', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'benh_nhan', 'bac_si_dam_nhan', 'trang_thai')

class FileKetQuaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileKetQua
        fields = ('id', 'file', 'thoi_gian_tao')

class FileKetQuaChuyenKhoaSerializer(serializers.ModelSerializer):
    file_ket_qua = FileKetQuaSerializer(source='file')
    class Meta:
        model = FileKetQuaChuyenKhoa
        fields = ('id', 'file_ket_qua')

class FileKetQuaTongQuatSerializer(serializers.ModelSerializer):
    file_ket_qua = FileKetQuaSerializer(source='file')
    class Meta:
        model = FileKetQuaTongQuat
        fields = ('id', 'file_ket_qua')

class KetQuaChuyenKhoaSerializer(serializers.ModelSerializer):
    file_chuyen_khoa = FileKetQuaChuyenKhoaSerializer(many=True, source='file_ket_qua_chuyen_khoa')
    class Meta:
        model = KetQuaChuyenKhoa
        fields = ('id', 'ma_ket_qua', 'mo_ta', 'ket_luan', 'file_chuyen_khoa')

class KetQuaTongQuatSerializer(serializers.ModelSerializer):
    file_tong_quat = FileKetQuaTongQuatSerializer(source='file_ket_qua_tong_quat', many=True)
    kq_chuyen_khoa = KetQuaChuyenKhoaSerializer(source='ket_qua_chuyen_khoa', many=True)
    class Meta:
        model = KetQuaTongQuat
        fields = ('id', 'ma_ket_qua', 'mo_ta', 'ket_luan', 'file_tong_quat', 'kq_chuyen_khoa')


        
class DonThuocSerializer(serializers.ModelSerializer):
    bac_si_ke_don = UserSerializer()
    benh_nhan = UserSerializer()
    class Meta:
        model = DonThuoc
        fields = '__all__'
        
class HoaDonThuocSerializer(serializers.ModelSerializer):
    don_thuoc = DonThuocSerializer()
    tong_tien = serializers.CharField(source='get_don_gia')
    class Meta:
        model = HoaDonThuoc
        fields = '__all__'

class TrangThaiDonThuocSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrangThaiDonThuoc
        fields = ('id', 'trang_thai')

class HoaDonThuocSerializerSimple(serializers.ModelSerializer):
    benh_nhan = UserSerializer()
    bac_si_ke_don = UserSerializer()
    trang_thai = TrangThaiDonThuocSerializer()
    trang_thai_thanh_toan = serializers.CharField(source='check_thanh_toan')
    class Meta:
        model = DonThuoc
        fields = (
            'id',
            'ma_don_thuoc',
            'chuoi_kham',
            'benh_nhan',
            'benh_nhan_vang_lai',
            'bac_si_ke_don',
            'trang_thai',
            'ly_do_chinh_sua',
            'thoi_gian_tao',
            'thoi_gian_cap_nhat',
            'trang_thai_thanh_toan',
        )


class PhanKhoaKhamDichVuSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhanKhoaKham
        fields = ('id', 'chuoi_kham', 'benh_nhan', 'bac_si_lam_sang', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'dich_vu_kham')

# class PhongChucNangSerializer(serializers.ModelSerializer):
#     dich_vu_kham = DichVuKhamSerializer()
#     danh_sach_benh_nhan = PhanKhoaKhamDichVuSerializer(source='danh_sach_benh_nhan_theo_dich_vu_kham', many=
#     True)
#     class Meta:
#         model = PhongChucNang
#         fields = ('id', 'dich_vu_kham', 'ten_phong_chuc_nang', 'danh_sach_benh_nhan')

class PhongChucNangSerializerSimple(serializers.ModelSerializer):
    bac_si_phu_trach = UserSerializer()
    thoi_gian_tao = serializers.CharField(source='get_thoi_gian_tao')
    thoi_gian_cap_nhat = serializers.CharField(source='get_thoi_gian_cap_nhat')
    class Meta:
        model = PhongChucNang
        fields = "__all__"



class KetQuaChuyenKhoaSerializer(serializers.ModelSerializer):
    file_chuyen_khoa = FileKetQuaChuyenKhoaSerializer(many=True, source='file_ket_qua_chuyen_khoa')
    ten_dich_vu = serializers.CharField(source="get_ten_dich_vu")
    class Meta:
        model = KetQuaChuyenKhoa
        fields = (
            'id',
            'ten_dich_vu',
            'ma_ket_qua', 
            'mo_ta', 
            'ket_luan', 
            'file_chuyen_khoa',
            'chi_so',
            'html'

        )

class FileKetQuaTongQuatSerializer(serializers.ModelSerializer):
    file_ket_qua = FileKetQuaSerializer(source='file')
    class Meta:
        model = FileKetQuaTongQuat
        fields = ('id', 'file_ket_qua')

class KetQuaTongQuatSerializer(serializers.ModelSerializer):
    file_tong_quat = FileKetQuaTongQuatSerializer(source='file_ket_qua_tong_quat', many=True)
    kq_chuyen_khoa = KetQuaChuyenKhoaSerializer(source='ket_qua_chuyen_khoa', many=True)
    class Meta:
        model = KetQuaTongQuat
        fields = ('id', 'ma_ket_qua', 'mo_ta', 'ket_luan', 'file_tong_quat', 'kq_chuyen_khoa')

class DonThuocSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonThuoc
        fields = '__all__'

class DichVuKhamPhanKhoaSerializer(serializers.ModelSerializer):
    phong_chuc_nang = PhongChucNangSerializerSimple()
    class Meta:
        model = DichVuKham
        fields = ('id', 'ma_dvkt', 'ten_dvkt', 'ma_cosokcb', 'phong_chuc_nang')


class UserSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'ho_ten', 'so_dien_thoai')


class ChuoiKhamUserSerializer(serializers.ModelSerializer):
    bac_si_dam_nhan = UserSerializerSimple()
    class Meta:
        model = ChuoiKham
        fields = ('id', 'bac_si_dam_nhan', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc')

class LichHenKhamUserSerializer(serializers.ModelSerializer):
    trang_thai = TrangThaiLichHenSerializer()
    chuoi_kham = ChuoiKhamUserSerializer(source='danh_sach_chuoi_kham', many=True)
    class Meta:
        model = LichHenKham
        fields = ('id', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'trang_thai', 'chuoi_kham')


class LichHenKhamSerializerSimple(serializers.ModelSerializer):
    trang_thai = TrangThaiLichHenSerializer()
    class Meta:
        model = LichHenKham
        fields = ('id', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'trang_thai')

class BookLichHenKhamSerializer(serializers.Serializer):
    benh_nhan = serializers.CharField()
    thoi_gian_bat_dau = serializers.CharField()
    # class Meta:
    #     model = LichHenKham
    #     fields = ('benh_nhan', 'thoi_gian_bat_dau')

class DanhSachDonThuocSerializer(serializers.ModelSerializer):
    bac_si_ke_don = UserSerializerSimple()
    class Meta:
        model = DonThuoc
        fields = ('id', 'ma_don_thuoc', 'bac_si_ke_don')

class DonThuocSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonThuoc
        fields = '__all__'


class DanhSachPhanKhoaSerializer(serializers.ModelSerializer):
    dich_vu_kham = DichVuKhamPhanKhoaSerializer()
    trang_thai = TrangThaiKhoaKhamSerializer()
    class Meta:
        model = PhanKhoaKham
        fields = ('id', 'priority', 'dich_vu_kham', 'trang_thai')

class UserSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'ho_ten', 'so_dien_thoai')


class ChuoiKhamUserSerializer(serializers.ModelSerializer):
    bac_si_dam_nhan = UserSerializerSimple()
    class Meta:
        model = ChuoiKham
        fields = ('id', 'bac_si_dam_nhan', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc')

class LichHenKhamUserSerializer(serializers.ModelSerializer):
    trang_thai = TrangThaiLichHenSerializer()
    chuoi_kham = ChuoiKhamUserSerializer(source='danh_sach_chuoi_kham', many=True)
    class Meta:
        model = LichHenKham
        fields = ('id', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'trang_thai', 'chuoi_kham')


class LichHenKhamSerializerSimple(serializers.ModelSerializer):
    trang_thai = TrangThaiLichHenSerializer()
    class Meta:
        model = LichHenKham
        fields = ('id', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'trang_thai', 'ly_do', 'loai_dich_vu')

class BookLichHenKhamSerializer(serializers.Serializer):

    benh_nhan = serializers.CharField()
    thoi_gian_bat_dau = serializers.CharField()
    loai_dich_vu = serializers.CharField()
    ly_do = serializers.CharField()

    # class Meta:
    #     model = LichHenKham
    #     fields = ('benh_nhan', 'thoi_gian_bat_dau')

class DanhSachDonThuocSerializer(serializers.ModelSerializer):
    bac_si_ke_don = UserSerializerSimple()
    class Meta:
        model = DonThuoc
        fields = ('id', 'ma_don_thuoc', 'bac_si_ke_don')

class BaiDangSerializer(serializers.ModelSerializer):
    noi_dung_chinh = serializers.CharField(source='get_truncated_noi_dung_chinh')
    class Meta:
        model = BaiDang
        fields = "__all__"
        
class NhomVatTuSerializer(serializers.ModelSerializer):
    class Meta:
        model = NhomVatTu
        fields = "__all__"

class VatTuSerializer(serializers.ModelSerializer):
    don_gia = serializers.CharField(source='get_don_gia')
    don_gia_tt = serializers.CharField(source='get_don_gia_tt')
    so_luong_kha_dung = serializers.CharField(source='get_so_luong_kha_dung')
    nhom_vat_tu = NhomVatTuSerializer()
    nha_thau = CongTySerializer()
    class Meta:
        model = VatTu
        fields = '__all__'
        
        
# -------- MINH Update ---------

class UserUpdateInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'ho_ten', 'so_dien_thoai', 'email', 'cmnd_cccd', 'ngay_sinh', 'gioi_tinh', 'dia_chi', 'dan_toc', 'ma_so_bao_hiem')

class UserUpdateInfoRequestSerializer(serializers.Serializer):
    benh_nhan = serializers.CharField(required=True)
    ho_ten = serializers.CharField()
    so_dien_thoai = serializers.CharField(required=True)
    email = serializers.CharField()
    cmnd_cccd = serializers.CharField()
    ngay_sinh = serializers.CharField()
    gioi_tinh = serializers.CharField()
    dia_chi = serializers.CharField()
    dan_toc = serializers.CharField()
    ma_so_bao_hiem = serializers.CharField()

class UploadAvatarSerializer(serializers.Serializer):
    file_uploaded = serializers.FileField()
    class Meta:
        fields = ['file_uploaded']

class AppointmentUpdateDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = LichHenKham
        fields = ('loai_dich_vu', 'dia_diem', 'ly_do', 'thoi_gian_bat_dau',)

class UpdateLichHenKhamSerializer(serializers.Serializer):
    appointment_id = serializers.CharField()
    thoi_gian_bat_dau = serializers.CharField()
    loai_dich_vu = serializers.CharField()
    ly_do = serializers.CharField()
    dia_diem = serializers.CharField()

class DichVuKhamHoaDonSerializer(serializers.ModelSerializer):
    class Meta:
        model = DichVuKham
        fields = ('ma_dvkt', 'ten_dvkt', 'don_gia')

class HoaDonChuoiKhamThanhToanSerializer(serializers.ModelSerializer):
    dich_vu_kham = DichVuKhamHoaDonSerializer()
    class Meta:
        model = PhanKhoaKham
        fields = ('dich_vu_kham', 'bao_hiem', 'priority',)
        
class DanhSachDichVuSerializer(serializers.ModelSerializer):
    class Meta:
        model = DichVuKham
        fields = ('ma_dvkt', 'ten_dvkt', 'don_gia')

class HoaDonLamSangSerializer(serializers.ModelSerializer):
    lich_hen = LichHenKhamSerializer()
    # tong_tien = serializers.CharField(source='get_don_gia')
    class Meta:
        model = HoaDonLamSang
        fields = ('id', 'tong_tien', 'thoi_gian_tao', 'lich_hen')

class HoaDonLamSangSerializerFormatted(serializers.ModelSerializer):
    lich_hen = LichHenKhamSerializer()
    tong_tien = serializers.CharField(source='get_don_gia')
    class Meta:
        model = HoaDonLamSang
        fields = ('id', 'tong_tien', 'thoi_gian_tao', 'lich_hen')


# * -------------------- End -----------------------


# UPDATE BY LONG
class BacSiSerializer(serializers.ModelSerializer):
    class Meta: 
        model = User
        fields = '__all__'


class DanhSachBacSiSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta: 
        model = BacSi
        fields = '__all__'
# END
class DichVuKhamSerializerFormatted(serializers.ModelSerializer):
    don_gia = serializers.CharField(source='get_don_gia')
    don_gia_bhyt = serializers.CharField(source='get_don_gia_bhyt')
    phong_chuc_nang = PhongChucNangSerializerSimple()
    bao_hiem_dich_vu = serializers.CharField(source='bao_hiem')
    class Meta:
        model = DichVuKham
        exclude = ('bao_hiem',)

class DichVuKhamSerializer(serializers.ModelSerializer):
    phong_chuc_nang = PhongChucNangSerializerSimple()
    class Meta:
        model = DichVuKham
        fields = '__all__'

class PhanKhoaKhamSerializer(serializers.ModelSerializer):
    chuoi_kham = ChuoiKhamPhanKhoaSerializer()
    benh_nhan = UserSerializer()
    bac_si_lam_sang = UserSerializer()
    dich_vu_kham = DichVuKhamSerializer()
    trang_thai = TrangThaiKhoaKhamSerializer()
    class Meta:
        model = PhanKhoaKham
        fields = (
            'id','chuoi_kham', 
            'benh_nhan', 
            'bac_si_lam_sang', 
            'thoi_gian_bat_dau', 
            'thoi_gian_ket_thuc', 
            'dich_vu_kham',
            'trang_thai'
        )

class ChuoiKhamSerializer(serializers.ModelSerializer):
    phan_khoa_kham = PhanKhoaKhamSerializer(many=True)
    benh_nhan = UserSerializer()
    bac_si_dam_nhan = UserSerializer()
    class Meta:
        model = ChuoiKham
        fields = '__all__'
 
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['actions'] = ''
        return response

class HoaDonChuoiKhamSerializer(serializers.ModelSerializer):
    chuoi_kham = ChuoiKhamSerializer()
    class Meta:
        model = HoaDonChuoiKham
        fields = '__all__'

class HoaDonChuoiKhamSerializerSimple(serializers.ModelSerializer):
    benh_nhan = UserSerializer()
    bac_si_dam_nhan = UserSerializer()  
    trang_thai_thanh_toan = serializers.CharField(source='check_thanh_toan')
    thanh_toan_sau = serializers.BooleanField(source='lich_hen.thanh_toan_sau')
    class Meta:
        model = ChuoiKham
        fields = (
            'id', 
            'benh_nhan', 
            'bac_si_dam_nhan',
            'trang_thai',
            'thoi_gian_tao',
            'trang_thai_thanh_toan',
            'thanh_toan_sau',
        )

class DanhSachTinhTrangSerializer(serializers.ModelSerializer):
    class Meta:
        model = TinhTrangPhongKham
        fields = '__all__'

class DanhSachPhongKhamSerializer(serializers.ModelSerializer):
    tinh_trang = DanhSachTinhTrangSerializer()
    class Meta:
        model = PhongKham
        fields = '__all__'

class TinhTrangPhongKhamSerializer(serializers.ModelSerializer):
    class Meta:
        model = TinhTrangPhongKham
        fields = '__all__'

class PhongKhamSerializer(serializers.ModelSerializer):
    tinh_trang = TinhTrangPhongKhamSerializer()
    class Meta:
        model = PhongKham
        fields = '__all__'


# class BenhNhanBaoHiemSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ('ma_benh_nhan', 'ho_ten', 'ngay_sinh', 'gioi_tinh', 'dia_chi', 'ma_so_bao_hiem', 'ma_dkbd', 'gt_the_tu', 'gt_the_den', 'mien_cung_ct', )

class FilterChuoiKhamSerializer(serializers.ModelSerializer):
    ma_benh_nhan = serializers.CharField(source='benh_nhan.ma_benh_nhan')
    ho_ten = serializers.CharField(source='benh_nhan.ho_ten')
    ngay_sinh = serializers.CharField(source='benh_nhan.ngay_sinh')
    gioi_tinh = serializers.CharField(source='benh_nhan.gioi_tinh')
    dia_chi = serializers.CharField(source='benh_nhan.dia_chi')
    ma_the = serializers.CharField(source='benh_nhan.ma_so_bao_hiem')
    ma_dkbd = serializers.CharField(source='benh_nhan.ma_dkbd')
    gt_the_tu = serializers.CharField(source='benh_nhan.gt_the_tu')
    gt_the_den = serializers.CharField(source='benh_nhan.gt_the_den')
    mien_cung_ct = serializers.CharField(source='benh_nhan.mien_cung_ct')
    ly_do_vvien = serializers.CharField(source='lich_hen.ly_do_vvien')
    ma_benh = serializers.CharField(source='get_ma_benh')
    ten_benh = serializers.CharField(source='get_ten_benh')
    ngay_vao = serializers.CharField(source='lich_hen.thoi_gian_bat_dau')
    ngay_ra = serializers.CharField(source='lich_hen.thoi_gian_ket_thuc')
    so_ngay_dieu_tri = serializers.CharField(source='get_so_ngay_dieu_tri')
    ket_qua_dieu_tri = serializers.CharField(source='get_ket_qua_dieu_tri')
    ngay_ttoan = serializers.CharField(source='get_ngay_ttoan')
    t_thuoc = serializers.CharField(source='get_tien_thuoc')
    nam_qt = serializers.CharField(source='get_nam_qt')
    thang_qt = serializers.CharField(source='get_thang_qt')
    ma_loai_kcb = serializers.CharField(source='get_ma_loai_kcb')
    ma_khuvuc = serializers.CharField(source='benh_nhan.ma_khuvuc')
    ma_pttt_qt = serializers.CharField(source='get_ma_pttt_qt')
    can_nang = serializers.CharField(source='benh_nhan.can_nang')

    class Meta:
        model = ChuoiKham
        fields = (
            'ma_lk', 
            'ma_benh_nhan',
            'ho_ten', 
            'ngay_sinh',
            'gioi_tinh',
            'dia_chi',
            'ma_the', 
            'ma_dkbd',
            'gt_the_tu',
            'gt_the_den',
            'mien_cung_ct',  
            'ten_benh',
            'ma_benh',
            'ly_do_vvien',
            'ngay_vao',
            'ngay_ra',
            'so_ngay_dieu_tri', 
            'ket_qua_dieu_tri',
            'ngay_ttoan',
            't_thuoc',
            'nam_qt', 
            'thang_qt',
            'ma_loai_kcb',
            'ma_khuvuc',
            'ma_pttt_qt',
            'can_nang'
        )

class FilterDonThuocSerializer(serializers.ModelSerializer):
    ma_lk = serializers.CharField(source='don_thuoc.chuoi_kham.ma_lk')
    ma_thuoc = serializers.CharField(source='thuoc.ma_thuoc')
    ten_thuoc = serializers.CharField(source='thuoc.ten_thuoc')
    ma_nhom = serializers.CharField(source='thuoc.nhom_chi_phi.ma_nhom')
    don_vi_tinh = serializers.CharField(source='thuoc.don_vi_tinh')
    ham_luong = serializers.CharField(source='thuoc.ham_luong')
    duong_dung = serializers.CharField(source='thuoc.duong_dung')
    lieu_dung = serializers.CharField(source='ghi_chu')
    so_dang_ky = serializers.CharField(source='thuoc.so_dang_ky')
    tt_thau = serializers.CharField(source='thuoc.quyet_dinh')
    pham_vi = serializers.CharField(source='thuoc.pham_vi')
    tyle_tt = serializers.CharField(source='thuoc.tyle_tt')
    don_gia = serializers.CharField(source='thuoc.don_gia')
    thanh_tien = serializers.CharField(source='gia_ban')
    muc_huong = serializers.CharField(source='thuoc.muc_huong')
    t_nguonkhac = serializers.CharField(source='get_tt_nguon_khac')
    t_ngoaids = serializers.CharField(source='get_t_ngoaids')
    ngay_yl = serializers.CharField(source='get_ngay_yl')
    ma_pttt = serializers.CharField(source='get_ma_pttt')

    class Meta:
        model = KeDonThuoc
        fields = (
            'ma_lk',
            'ma_thuoc',
            'ma_nhom',
            'ten_thuoc',
            'don_vi_tinh',
            'ham_luong',
            'duong_dung',
            'lieu_dung',
            'so_dang_ky',
            'tt_thau',
            'pham_vi',
            'tyle_tt',
            'so_luong',
            'don_gia',
            'thanh_tien',
            'muc_huong',
            't_nguonkhac',
            't_ngoaids',
            'ngay_yl',
            'ma_pttt'
        )

class FilterDichVuSerializer(serializers.ModelSerializer):
    ma_lk = serializers.CharField(source='chuoi_kham.ma_lk')
    ma_dich_vu = serializers.CharField(source='dich_vu_kham.ma_dvkt')
    ma_vat_tu = serializers.CharField(source='get_ma_vat_tu')
    ma_nhom = serializers.CharField(source='dich_vu_kham.nhom_chi_phi.ma_nhom')
    ten_dich_vu = serializers.CharField(source='dich_vu_kham.ten_dvkt')
    so_luong = serializers.CharField(source='get_so_luong')
    don_gia = serializers.CharField(source='dich_vu_kham.don_gia')
    tyle_tt = serializers.CharField(source='dich_vu_kham.tyle_tt')
    thanh_tien = serializers.CharField(source='dich_vu_kham.don_gia')
    ma_benh = serializers.CharField(source='chuoi_kham.get_ma_benh')
    ngay_yl = serializers.CharField(source='get_ngay_yl')
    ngay_kq = serializers.CharField(source='get_ngay_kq')
    t_nguonkhac = serializers.CharField(source='get_t_nguonkhac')
    t_ngoaids = serializers.CharField(source='get_t_ngoaids')
    ma_pttt = serializers.CharField(source='get_ma_pttt')

    class Meta:
        model = PhanKhoaKham
        fields = (
            'ma_lk',
            'ma_dich_vu',
            'ma_vat_tu',
            'ma_nhom',
            'ten_dich_vu',
            'so_luong',
            'don_gia',
            'tyle_tt',
            'thanh_tien',
            't_nguonkhac',
            't_ngoaids',
            'ma_benh',
            'ngay_yl',
            'ngay_kq',
            'ma_pttt'
        )

class MauPhieuSerializer(serializers.ModelSerializer):
    class Meta:
        model = MauPhieu
        fields = '__all__'

class TatCaLichHenSerializer(serializers.ModelSerializer):
    trang_thai = TrangThaiLichHenSerializer()
    class Meta:
        model = LichHenKham
        fields = ('id', 'ma_lich_hen', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc', 'trang_thai')

class FilterHoaDonChuoiKhamBaoHiemSerializer(serializers.ModelSerializer):
    benh_nhan = serializers.CharField(source='get_benh_nhan')
    nam_sinh = serializers.CharField(source='chuoi_kham.benh_nhan.ngay_sinh')
    gioi_tinh = serializers.CharField(source='chuoi_kham.benh_nhan.gioi_tinh')
    ma_bhyt = serializers.CharField(source='chuoi_kham.benh_nhan.ma_so_bao_hiem')
    ma_dkbd = serializers.CharField(source='chuoi_kham.benh_nhan.ma_dkbd')
    ma_benh = serializers.CharField(source='get_ma_benh')
    ngay_kham = serializers.CharField(source='get_ngay_kham')
    tong_cong_1 = serializers.IntegerField(source='get_tong_cong')
    xet_nghiem = serializers.IntegerField(source='get_gia_xet_nghiem')
    cdha_tdcn = serializers.IntegerField(source='get_gia_cdha_tdcn')
    thuoc_1 = serializers.IntegerField(source='get_gia_thuoc_1')
    mau = serializers.IntegerField(source='get_gia_mau')
    ttpt = serializers.IntegerField(source='get_gia_ttpt')
    vtyt_1 = serializers.IntegerField(source='get_gia_vtyt_1')
    dvkt = serializers.IntegerField(source='get_gia_dvkt')
    thuoc_2 = serializers.IntegerField(source='get_gia_thuoc_2')
    vtyt_2 = serializers.IntegerField(source='get_gia_vtyt_2')
    
    tien_kham = serializers.IntegerField(source='get_tong_cong')
    van_chuyen = serializers.IntegerField(source='get_gia_van_chuyen')
    tu_chi_tra = serializers.IntegerField(source='get_tu_chi_tra')
    bao_hiem_tra = serializers.IntegerField(source='get_bao_hiem_tra')
    ngoai_ds = serializers.IntegerField(source='get_chi_phi_ngoai_ds')

    class Meta:
        model = HoaDonChuoiKham
        fields = (
            'benh_nhan',
            'gioi_tinh',
            'nam_sinh',
            'ma_bhyt',
            'ma_dkbd',
            'ma_benh',
            'ngay_kham',
            'tong_cong_1',
            'xet_nghiem',
            'cdha_tdcn',
            'thuoc_1',
            'mau',
            'ttpt',
            'vtyt_1',
            'dvkt',
            'thuoc_2',
            'vtyt_2',
            'tien_kham',
            'van_chuyen',
            'tu_chi_tra',
            'bao_hiem_tra',
            'ngoai_ds'
        )

class FilterDichVuKhamBaoHiemSerializer(serializers.ModelSerializer):

    class Meta:
        model = PhanKhoaKham
        fields = '__all__'

class DanhSachKetQuaChuoiKhamSerializer(serializers.ModelSerializer):
    benh_nhan = UserSerializerSimple()
    trang_thai = TrangThaiChuoiKhamSerializer()
    class Meta:
        model = ChuoiKham
        fields = '__all__'

class DanhSachThuocSerializerSimple(serializers.ModelSerializer):
    thuoc = ThuocSerializerSimple()
    class Meta:
        model = KeDonThuoc
        fields = '__all__'

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'

class WardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ward
        fields = '__all__'

class NhomChiSoTieuChuanSerializer(serializers.ModelSerializer):
    class Meta:
        model = NhomChiSoXetNghiem
        fields = '__all__'

class ChiTietChiSoXetNghiemSerializer(serializers.ModelSerializer):
    chi_so_binh_thuong_min = serializers.CharField(source='get_chi_so_binh_thuong_min')
    chi_so_binh_thuong_max = serializers.CharField(source='get_chi_so_binh_thuong_max')
    chi_so_binh_thuong = serializers.CharField(source='get_chi_so_binh_thuong')
    don_vi_do = serializers.CharField(source='get_don_vi_do')
    ghi_chu = serializers.CharField(source='get_ghi_chu')
    class Meta:
        model = ChiTietChiSoXetNghiem
        fields = (
            'id',
            'chi_so_binh_thuong_min',
            'chi_so_binh_thuong_max',
            'chi_so_binh_thuong',
            'don_vi_do',
            'ghi_chu'
        )

class ChiSoXetNghiemSerializer(serializers.ModelSerializer):
    chi_tiet = ChiTietChiSoXetNghiemSerializer()
    nhom_chi_so = NhomChiSoTieuChuanSerializer()
    class Meta:
        model = ChiSoXetNghiem
        fields = (
            'id',
            'chi_tiet',
            'ma_chi_so',
            'ten_chi_so',
            'dich_vu_kham',
            'doi_tuong_xet_nghiem',
            'nhom_chi_so',
        )


class KetQuaXetNghiemSerializer(serializers.ModelSerializer):
    # chi_so_xet_nghiem = ChiSoXetNghiemSerializer()
    dich_vu = serializers.CharField(source='get_ten_dvkt')
    chi_so_xet_nghiem = ChiSoXetNghiemSerializer()
    class Meta:
        model = KetQuaXetNghiem
        fields = (
            'dich_vu',
            'chi_so_xet_nghiem',
            'ket_qua_xet_nghiem',
            'danh_gia_chi_so',
            'danh_gia_ghi_chu',
        )

class PhieuKetQuaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HtmlKetQua
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = (
            'id', 
            'codename', 
            'name'
        )

class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'username', 
            'ho_ten', 
            'so_dien_thoai',
            'gioi_tinh',
            'cmnd_cccd',
            'chuc_nang',
            'ngay_sinh',
        )

class HoaDonNhapHangSerializer(serializers.ModelSerializer):
    nguoi_phu_trach = UserSerializerSimple()
    class Meta:
        model = HoaDonNhapHang
        fields=(
            'nguoi_phu_trach',
            'ma_hoa_don',
            'thoi_gian_tao',
        )
class NhapHangSerializer(serializers.ModelSerializer):
    thuoc = ThuocSerializerSimple()
    hoa_don = HoaDonNhapHangSerializer()
    class Meta:
        model = NhapHang
        fields= '__all__' 

class DichVuKhamPhanKhoaSerializer(serializers.ModelSerializer):
    phong_chuc_nang = serializers.CharField(source='get_ten_phong_chuc_nang')
   
    class Meta:
        model = DichVuKham
        fields = (
            'id', 
            'ten_dvkt', 
            'ma_dvkt',
            'phong_chuc_nang',
        )

# class DanhSachPhanKhoaSerializer(serializers.ModelSerializer):
#     dich_vu_kham = DichVuKhamPhanKhoaSerializer()
#     class Meta:
#         model = PhanKhoaKham
#         fields = (
#             'id',
#             'dich_vu_kham',
#             'bao_hiem',
#         )