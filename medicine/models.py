from clinic.models import DuongDungThuoc, GoiThau, NhomChiPhi
from datetime import time
import decimal
from finance.models import HoaDonThuoc, HoaDonVatTu
from django.db import models
import uuid
from django.utils import timezone
from bulk_update_or_create import BulkUpdateOrCreateQuerySet
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

# User = get_user_model()

class CongTy(models.Model):
    TYPE_CHOICES_LOAI_CUNG = (
        ('thuoc', 'Thuốc'),
        ('vat_tu', 'Vật Tư'),
    ) 
    id = models.AutoField(primary_key=True)
    
    ten_cong_ty = models.CharField(max_length=255, verbose_name="Tên Công Ty")
    giay_phep_kinh_doanh = models.CharField(max_length=255, verbose_name="Giấy phép kinh doanh", null=True, blank=True)
    dia_chi = models.CharField(max_length=255, verbose_name="Địa chỉ", null=True, blank=True)
    so_lien_lac = models.CharField(max_length=255, verbose_name="Số liên lạc", null=True, blank=True)
    email = models.CharField(max_length=255, verbose_name="Email công ty", null=True, blank=True)
    mo_ta = models.CharField(max_length=255, verbose_name="Mô tả công ty", null=True, blank=True)
    loai_cung = models.CharField(max_length=255, choices=TYPE_CHOICES_LOAI_CUNG, null=True, blank = True)
    
    ngay_gio_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giờ tạo")
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Công Ty'
        verbose_name_plural = 'Công Ty'
        permissions = (
            ('can_add_company', 'Thêm nguồn cung'),
            ('can_change_company', 'Thay đổi nguồn cung'),
            ('can_view_company', 'Xem nguồn cung'),
            ('can_delete_company', 'Xóa nguồn cung'),
            ('can_export_list_of_company', 'Xuất danh sách nguồn cung')
        )

    def __str__(self):
        return self.ten_cong_ty
# class LoaiThuoc(models.Model): 
    
#     loai_thuoc = models.CharField(max_length=255, choices=TYPE_CHOICES)
class NhomThau(models.Model):
    ten_nhom_thau = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.ten_nhom_thau

class Thuoc(models.Model):
    PHAM_VI = (
        ("1", "Thuốc trong phạm vi hưởng BHYT"),
        ("2", "Thuốc ngoài phạm vi hưởng BHTY"),
    )
    TYPE_CHOICES_LOAI_THUOC = (
        ('1', 'Tân Dược'),
        ('2', 'Chế phẩm YHCT'),
        ('3', 'Vị thuốc YHCT'),
        ('4', 'Phóng xạ'),
        ('5', 'Thực phẩm bảo vệ sức khỏe'),
        ('6', 'Vật Tư Y Tế'),
    )
    TYPE_CHOICES_LOAI_THAU = (
        ('1', 'Thầu tập trung'),
        ('2', 'Thầu riêng tại BV')
    )

    id = models.AutoField(primary_key=True)
    stt = models.CharField(max_length=50, null=True, blank=True)
    nhom_thuoc = models.ManyToManyField("NhomThuoc", related_name='nhom_thuoc')
    ma_thuoc = models.CharField(max_length=50, blank=True, null=True)
    ma_hoat_chat = models.CharField(max_length=15, null=True, blank=True, verbose_name="Mã hoạt chất")
    ten_hoat_chat = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên hoạt chất")
    duong_dung = models.CharField(max_length=255, null=True, blank=True, verbose_name="Đường dùng")
    # duong_dung = models.ForeignKey(DuongDungThuoc, on_delete=models.SET_NULL, null=True, blank=True)
    ham_luong = models.CharField(max_length=255, null=True, blank=True, verbose_name="Hàm lượng")
    ten_thuoc = models.CharField(max_length=255, null=True, blank=True, verbose_name="Tên thuốc")    
    # ma_thuoc = models.CharField(max_length=200, null=True, blank=True, verbose_name="Mã thuốc") # mã thuốc được sử dụng khi tồn tại 2 loại thuốc giống nhau nhưng khác công ty
    # loai_thuoc = models.CharField(max_length=100, null=True, blank=True, verbose_name="Loại thuốc") # có rất nhiều loại thuốc khác nhau: viên nén/viên nang/siro/....
    so_dang_ky = models.CharField(max_length=50, null=True, blank=True, verbose_name="Số đăng ký")
    dong_goi = models.CharField(max_length=255, null=True, blank=True, verbose_name="Đóng gói")
    don_vi_tinh = models.CharField(max_length=255, null=True, blank=True, verbose_name="Đơn vị tính")
    don_gia = models.IntegerField(null=True, verbose_name="Đơn giá")
    don_gia_tt = models.IntegerField(null=True, verbose_name="Đơn giá thành tiền")
    gia_bhyt = models.IntegerField(null=True, verbose_name="Giá bảo hiểm y tế")
    so_lo = models.CharField(max_length=255, blank=True, null=True, verbose_name="Số Lô")
    so_luong_kha_dung = models.IntegerField(verbose_name="Số lượng khả dụng", null=True, blank=True) # Số lượng thuốc khả dụng sau khi đã bán hoặc trả lại thuốc 
    # Để kiểm soát và duy trì truy xuất nguồn gốc, số lô được chỉ định và cũng giúp kiểm tra thời hạn sử dụng và các vấn đề khác
    # Thuốc có thời hạn sử dụng là 3 năm nên tùy theo nhu cầu sử dụng và cách tiêu dùng mà cơ sở sản xuất có lịch sản xuất.. 
    ma_cskcb = models.CharField(max_length=50, null=True, blank=True)
    hang_sx = models.CharField(max_length=255, null=True, blank=True)
    nuoc_sx = models.CharField(max_length=100, null=True, blank=True)
    cong_ty = models.ForeignKey(CongTy, on_delete=models.CASCADE, related_name="thuoc_cong_ty", null=True, blank=True)
    quyet_dinh = models.CharField(max_length=255, null=True, blank=True)
    loai_thuoc = models.CharField(max_length=255, choices=TYPE_CHOICES_LOAI_THUOC, null=True, blank = True)
    cong_bo = models.CharField(max_length=50, null=True, blank=True)
    loai_thau = models.CharField(max_length=255, choices=TYPE_CHOICES_LOAI_THAU, null = True, blank = True)
    nhom_thau = models.ForeignKey(NhomThau, on_delete=models.SET_NULL, null=True, blank=True)
    bao_hiem = models.BooleanField(default=False, null=True, blank=True)
    # so_ke_tai_quay = models.CharField(max_length=255, null=True, blank=True, verbose_name="Số Kệ") # Để có thể biết được vị trí thuốc này đang được đặt chỗ nào trong quầy thuốc.
    han_su_dung = models.DateField(null=True, blank=True) # Hạn sử dụng
    ngay_san_xuat = models.DateField(null=True, blank=True) # Ngày sản xuất

    nhom_chi_phi = models.ForeignKey(NhomChiPhi, on_delete=models.SET_NULL, null=True, blank=True)
    pham_vi = models.CharField(max_length=5, choices=PHAM_VI, null=True, blank=True)
    tyle_tt = models.IntegerField(null=True, blank=True)
    muc_huong = models.IntegerField(null=True, blank=True)

    ngay_gio_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giờ tạo", null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True, null=True, blank=True)
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    # UPDATE
    diem_tich = models.PositiveIntegerField(null=True, blank=True)
    # END

    class Meta:
        verbose_name = "Thuốc"
        verbose_name_plural = "Thuốc"
        permissions = (
            ('can_add_medicine', 'Thêm thuốc'),
            ('can_change_medicine', 'Thay đổi thuốc'),
            ('can_view_medicine', 'Xem thuốc'),
            ('can_delete_medicine', 'Xóa thuốc'),
            ('can_view_import_medicine_price', 'Xem giá thuốc nhập'),
            ('can_view_export_medicine_price', 'Xem giá thuốc bán ra'),
            ('can_export_medicine_list', 'Xuất danh sách thuốc'),
        )

    def __str__(self):
        return self.ten_thuoc

    @property
    def kha_dung(self):
        if self.so_luong_kha_dung is not None:
            return self.so_luong_kha_dung > 0
        else:
            return False

    @property
    def check_expiration(self):
        six_months_later = date.today() + relativedelta(months=+6)
        if not self.han_su_dung:
            return False
        else:
            expiration = datetime.strptime(str(self.han_su_dung), '%Y-%m-%d').date()
            if expiration <= six_months_later:
                return True 
            else: 
                return False

    @property
    def check_loai_thuoc(self):
        if self.loai_thuoc == '5':
            return True
        else:
            return False

    def get_don_gia(self):
        try:
            don_gia = "{:,}".format(int(self.don_gia))
        except ValueError:
            don_gia = "{:,}".format(float(self.don_gia))
        return don_gia

    def get_don_gia_tt(self):
        try:
            don_gia_tt = "{:,}".format(int(self.don_gia_tt))
        except ValueError:
            don_gia_tt = "{:,}".format(float(self.don_gia_tt))
        return don_gia_tt

    def get_so_luong_kha_dung(self):
        if self.so_luong_kha_dung is not None:
            so_luong_kha_dung = "{:,}".format(self.so_luong_kha_dung)
        else:
            so_luong_kha_dung = 0
        return so_luong_kha_dung

    def get_bao_hiem(self):
        if self.bao_hiem:
            return "True"
        else:
            return "False"


class NhomThuoc(models.Model):
    ma_nhom = models.CharField(max_length=255, null=True, blank=True)
    ten_nhom = models.CharField(max_length=255, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True, auto_now_add=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True, auto_now=True)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Nhóm Thuốc'
        verbose_name_plural = 'Nhóm Thuốc'

    def __str__(self):
        return self.ten_nhom

class GiaThuoc(models.Model):
    """ Bảng Giá sẽ lưu trữ tất cả giá của thuốc"""
    id_thuoc = models.OneToOneField(Thuoc, on_delete=models.PROTECT, null=True, blank=True, related_name="gia_thuoc")
    gia = models.DecimalField(max_digits=10, decimal_places=3)   
    thoi_gian_tao = models.DateTimeField(null=True, blank=True, editable=False)
    thoi_gian_chinh_sua = models.DateTimeField(null=True, blank=True)

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_chinh_sua = timezone.now()
        return super(GiaThuoc, self).save(*agrs, **kwargs)
    
class BaoHiemThuoc(models.Model):
    id_thuoc = models.OneToOneField(Thuoc, on_delete=models.PROTECT, null=True, blank=True, related_name="bao_hiem_thuoc")
    muc_bao_hiem = models.PositiveIntegerField() 
    thoi_gian_tao = models.DateTimeField(null=True, blank=True, editable=False)
    thoi_gian_chinh_sua = models.DateTimeField(null=True, blank=True)

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_chinh_sua = timezone.now()
        return super(BaoHiemThuoc, self).save(*agrs, **kwargs)

class TrangThaiDonThuoc(models.Model):
    trang_thai = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Trạng Thái Đơn Thuốc"
        verbose_name_plural = "Trạng Thái Đơn Thuốc"

def get_default_trang_thai_don_thuoc():
    return TrangThaiDonThuoc.objects.get_or_create(trang_thai="Đang Chờ")[0]

class DonThuoc(models.Model):
    chuoi_kham = models.ForeignKey("clinic.ChuoiKham", on_delete=models.CASCADE, related_name="don_thuoc_chuoi_kham", null=True, blank=True)
    benh_nhan = models.ForeignKey("clinic.User", on_delete=models.CASCADE, related_name="don_thuoc", null=True, blank=True)
    benh_nhan_vang_lai = models.CharField(max_length=255, null=True, blank=True)
    bac_si_ke_don = models.ForeignKey("clinic.User", on_delete=models.CASCADE, related_name="bac_si_ke_don", null=True, blank=True)
    ma_don_thuoc = models.CharField(max_length=50, unique=True)
    trang_thai = models.ForeignKey(TrangThaiDonThuoc, on_delete=models.CASCADE, null=True)
    ly_do_chinh_sua = models.TextField(null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Đơn Thuốc"
        verbose_name_plural = "Đơn Thuốc"
        permissions = (
            ('can_add_prescription', 'Thêm đơn thuốc'),
            ('can_change_prescription', 'Thay đổi đơn thuốc'),
            ('can_view_prescription', 'Xem đơn thuốc'),
            ('can_delete_prescription', 'Xóa đơn thuốc'),
            ('can_print_prescription', 'In đơn thuốc'),

        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(DonThuoc, self).save(*args, **kwargs)

    @property
    def check_tphtdt(self):
        tphtdt = False
        danh_sach_ke_don = self.ke_don.all()
        for i in danh_sach_ke_don:
            if i.thuoc.check_loai_thuoc:
                tphtdt = True
        return tphtdt

    def check_da_thanh_toan(self):
        hoan_thanh = TrangThaiDonThuoc.objects.filter(trang_thai='Đã Thanh Toán').first()
        if self.trang_thai == hoan_thanh:
            return True
        else:
            return False

    @property
    def check_cho_thanh_toan(self):
        cho_thanh_toan = TrangThaiDonThuoc.objects.filter(trang_thai='Chờ Thanh Toán').first()
        if self.trang_thai == cho_thanh_toan:
            return True
        else:
            return False
    
    @property
    def check_hoan_thanh(self):
        hoan_thanh = TrangThaiDonThuoc.objects.filter(trang_thai='Hoàn Thành').first()
        if self.trang_thai == hoan_thanh:
            return True
        else:
            return False

    def check_thanh_toan(self):
        checkout = False
        try:
            checkout = (self.hoa_don_thuoc is not None)
        except HoaDonThuoc.DoesNotExist:
            pass
        return checkout

class LichSuTrangThaiDonThuoc(models.Model):
    don_thuoc = models.ForeignKey(DonThuoc, on_delete=models.CASCADE)
    trang_thai_don_thuoc = models.ForeignKey(TrangThaiDonThuoc, on_delete=models.CASCADE)
    chi_tiet_trang_thai = models.TextField()

    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

class KeDonThuoc(models.Model):
    don_thuoc = models.ForeignKey(DonThuoc, on_delete=models.CASCADE, null=True, related_name="ke_don")
    
    thuoc = models.ForeignKey(Thuoc, on_delete=models.CASCADE, null=True, blank=True)
    cach_dung = models.TextField()
    so_luong = models.PositiveIntegerField()
    ghi_chu = models.TextField()
    bao_hiem = models.BooleanField(default=False)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Kê Đơn Thuốc"
        verbose_name_plural = "Kê Đơn Thuốc"
        permissions = (
            ('can_prescribe', 'Kê đơn'),
        )

    def gia_thuoc_theo_bao_hiem(self):
        gia_ban = self.thuoc.gia_thuoc.gia
        if self.bao_hiem:    
            tong_tien = gia_ban * decimal.Decimal((1 - (self.thuoc.bao_hiem_thuoc.muc_bao_hiem / 100))) * self.so_luong
        else: 
            tong_tien = gia_ban * self.so_luong
        return tong_tien

    def gia_ban(self):
        gia_ban = self.thuoc.don_gia_tt
        tong_tien = int(gia_ban) * self.so_luong
        return tong_tien

    def get_thanh_tien(self):
        gia_thuoc = self.thuoc.don_gia_tt
        so_luong = self.so_luong
        thanh_tien = so_luong * int(gia_thuoc)
        thanh_tien = "{:,}".format(int(thanh_tien))
        return thanh_tien
    
    def get_tong_tien(self):
        gia_thuoc = self.thuoc.don_gia_tt
        so_luong = self.so_luong
        thanh_tien = so_luong * int(gia_thuoc)
        return int(thanh_tien)

    def get_tong_tien_bao_hiem(self):
        if self.bao_hiem:
            gia_thuoc = self.thuoc.don_gia_tt
            so_luong = self.so_luong
            thanh_tien = so_luong * int(gia_thuoc)
            return int(thanh_tien)
        else:
            return 0

    def get_tt_nguon_khac(self):
        return 0

    def get_t_ngoaids(self):
        return 0

    def get_ma_pttt(self):
        return 1

    def get_ngay_yl(self):
        return self.don_thuoc.thoi_gian_tao.strftime("%Y%m%d%H%M")


class ThuocLog(models.Model):

    """ 
        IN: In operation happens in real scenario is when items are added to the stock
        OUT: Out operation is used to keep track of why the item is being removed from the stock(sales, return to vendors, etc.)
    """

    IN = "I"
    OUT = "O"
    OPERATIONS = (
        (IN, "In"),
        (OUT, "Out"),
    )
    thuoc = models.ForeignKey(Thuoc, on_delete=models.CASCADE, related_name="thuoc_logs", verbose_name="Thuốc")
    ngay = models.DateTimeField(verbose_name="Ngày giờ")
    quy_trinh = models.CharField(max_length=1, choices=OPERATIONS, verbose_name="Quy trình")
    so_luong = models.IntegerField(default=0, verbose_name="Số lượng")

    bao_hiem = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Thuốc Log"
        verbose_name_plural = "Thuốc Log"

    def __str__(self):
        return self.thuoc.ten_thuoc + ' --> ' + self.quy_trinh

class ChiTietThuoc(models.Model):
    # https://www.drugs.com/article/pharmaceutical-salts.html

        # Theo Drugs.com, các dạng muối phổ biến nhất trong dược phẩm, theo đơn đặt hàng và các sản phẩm ví dụ, là:
        # 1. Hydrochloride (Cetirizine & Benadryl)
        # 2. Sodium (saline)
        # 3. Sulfate (Garamycin, Septopa, & Epsom)
        # 4. Acetate (Lithium)
        # 5. Phosphate/diphosphate (Visicol)
        # 6. Chloride (Bisacodyl)
        # 7. Potassium (Klor-Con & Gen-K)
        # 8. Maleate (Enalapril)
        # 9. Calcium (Caltrate & Tums)
        # 10. Citrate (Bicitra & Cytra-K)
        # 11. Mesylate (Pexeva & Cogentin)
        # 12. Nitrate (Dilatrate & ISMO)
        # 13. Tartrate (Lopressor & Zolpidem)
        # 14. Aluminum (Maalox & Amphojel)
        # 15. Gluconate (Ferrlecit)
 
    # lý do tại sao có bảng Thành phần Thuốc là vì thuốc
     # thường được gọi bằng cả "tên thuốc gốc" và "tên muối" của chúng
     # Một ví dụ là cách tốt nhất để giải thích câu hỏi này.
     # Phiên bản không kê đơn (không kê đơn hoặc OTC) của omeprazole theo toa (Prilosec) là omeprazole magie (Prilosec OTC).
     # Prilosec OTC là muối magiê của omeprazole ở dạng viên nang phóng thích chậm.

    id = models.AutoField(primary_key=True)
    id_thuoc = models.ForeignKey(Thuoc, on_delete=models.CASCADE, verbose_name="Thuốc")
    ten_muoi = models.CharField(max_length=255, verbose_name="Tên thuốc con")
    ham_luong = models.CharField(max_length=255, verbose_name="Hàm lượng")
    mo_ta = models.CharField(max_length=255, verbose_name="Mô tả")
    ngay_gio_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giờ tạo")
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        verbose_name = 'Chi Tiết Thuốc'
        verbose_name_plural = 'Chi Tiết Thuốc'


class NhomVatTu(models.Model):
    # UPDATE
    ma_nhom_vtyt = models.CharField(max_length=50, blank=True, null=True)
    # END
    ten_nhom_vtyt = models.CharField(max_length=255, blank=True, null=True)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True, auto_now_add=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True, auto_now=True)
    objects = models.Manager()

    class Meta:
        verbose_name = 'Nhóm Vật Tư'
        verbose_name_plural = 'Nhóm Vật Tư'
    
    def nhom_vat_tu(self):
        return self.ten_nhom_vtyt

class VatTu(models.Model):
    PHAM_VI = (
        ("1", "Vật tư trong phạm vi hưởng BHYT"),
        ("2", "Vật tư ngoài phạm vi hưởng BHTY"),
    )

    TYPE_CHOICES_LOAI_THAU = (
        ('1', 'Thầu tập trung'),
        ('2', 'Thầu riêng tại BV')
    )
    stt = models.CharField(max_length=50, null=True, blank=True)
    ma_hieu = models.CharField(max_length=30, blank=True, null=True)
    ma_vtyt_bv = models.CharField(max_length=100, blank=True, null=True)
    ten_vtyt_bv = models.CharField(max_length=250, null=True, blank=True)
    quy_cach = models.CharField(max_length=100, null=True, blank=True)
    hang_sx = models.CharField(max_length=100, null=True, blank=True)
    nuoc_sx = models.CharField(max_length=100, null=True, blank=True)
    don_vi_tinh = models.CharField(max_length=20, null=True, blank=True)
    bao_hiem = models.BooleanField(default=False)
    don_gia = models.CharField(max_length=50, null=True, verbose_name="Đơn giá")
    don_gia_tt = models.CharField(max_length=50, null=True, verbose_name="Đơn giá thành tiền")
    nhom_vat_tu = models.ForeignKey(NhomVatTu, on_delete=models.CASCADE, related_name="nhom_vat_tu", null=True, blank=True)
    nha_thau = models.ForeignKey(CongTy, on_delete=models.CASCADE, related_name="vat_tu_cong_ty", null=True, blank=True)
    quyet_dinh = models.CharField(max_length=20, null=True, blank=True)
    cong_bo = models.CharField(max_length=10, null=True, blank=True)
    dinh_muc = models.CharField(max_length=10, null=True, blank=True)
    so_luong_kha_dung = models.IntegerField(verbose_name="Số lượng khả dụng")
    loai_thau = models.CharField(max_length=255, choices=TYPE_CHOICES_LOAI_THAU, null=True, blank=True)

    pham_vi = models.CharField(max_length=5, choices=PHAM_VI, null=True, blank=True)
    goi_vtyt = models.ForeignKey(GoiThau, on_delete=models.SET_NULL, null=True, blank=True)
    tyle_tt = models.IntegerField(null=True, blank=True)
    muc_huong = models.IntegerField( null=True, blank=True)

    ngay_gio_tao = models.DateTimeField(auto_now_add=True, verbose_name="Ngày giờ tạo")
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True)
    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Vật Tư"
        verbose_name_plural = "Vật Tư"
        permissions = (
            ('can_add_medical_supplies', 'Thêm vật tư y tế'),
            ('can_change_medical_supplies', 'Thay đổi vật tư y tế'),
            ('can_view_medical_supplies', 'Xem vật tư y tế'),
            ('can_delete_medical_supplies', 'Xóa vật tư y tế'),
            ('can_export_medical_supplies_list', 'Xuất danh sách vật tư y tế'),
            ('can_listed_supplies_at_the_end_of_month', 'Thống kê vật tư cuối tháng'),
            ('can_add_supplies_using_excel_file', 'Thêm vật tư bằng Excel File'),
        )

    def __str__(self):
        return self.ten_vtyt_bv

    @property
    def kha_dung(self):
        return self.so_luong_kha_dung > 0

    def get_don_gia(self):
        if self.don_gia is not None:
            don_gia = "{:,}".format(int(self.don_gia))
        else:
            don_gia = '-'
        return don_gia

    def get_don_gia_tt(self):
        if self.don_gia_tt is not None:
            don_gia_tt = "{:,}".format(int(self.don_gia_tt))
        else:
            don_gia_tt = '-'
        return don_gia_tt

    def get_so_luong_kha_dung(self):
        if self.so_luong_kha_dung is not None:
            so_luong_kha_dung = "{:,}".format(int(self.so_luong_kha_dung))
        else:
            so_luong_kha_dung = '-'
        return so_luong_kha_dung

class KeVatTu(models.Model):
    hoa_don_vat_tu = models.ForeignKey(HoaDonVatTu, on_delete=models.CASCADE, null=True, blank=True, related_name="ke_don")
    # bac_si_lam_sang = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name="bac_si_lam_sang")
    # benh_nhan = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user), related_name="don_thuoc_benh_nhan")
    vat_tu = models.ForeignKey(VatTu, on_delete=models.CASCADE, null=True, blank=True)
    so_luong = models.PositiveIntegerField(null=True, blank=True)
    bao_hiem = models.BooleanField(default=False)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        verbose_name = "Kê Vật Tư "
        verbose_name_plural = "Kê Vật Tư"
        permissions = (
            ('can_list_medical_supplies', 'Kê vật tư'),
        )
