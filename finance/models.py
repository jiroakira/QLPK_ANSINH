from django.db import models
from django.utils import timezone

class HoaDonThuoc(models.Model):
    # benh_nhan = models.ForeignKey(NguoiDung, on_delete=models.SET(get_sentinel_user))
    """ 
    * Bảng hóa đơn thuốc sẽ lưu trữ lại hóa đơn của tất cả người dùng
    
    @field chuoi_kham: mối quan hệ 1-1 với Chuỗi Khám, vì một chuỗi khám sẽ chỉ có một hóa đơn
    @field ma_hoa_don: mã hóa đơn này sẽ do bác sĩ tự quy định, bác sĩ có thể quy định mã hóa đơn này theo người bệnh và thời gian họ khám để dễ dàng phân biệt
    @field tong_tien: tổng số tiền của các thuốc mà bệnh nhân đã được kê đơn
    @field thoi_gian_tao: thời gian hóa đơn được tạo
    @field thoi_gian_cap_nhat: thời gian hóa đơn được cập nhật
    """
    don_thuoc = models.OneToOneField("medicine.DonThuoc", on_delete=models.CASCADE, null=True, related_name='hoa_don_thuoc')
    nguoi_thanh_toan = models.ForeignKey("clinic.User", on_delete=models.SET_NULL, null=True, blank=True)
    ma_hoa_don = models.CharField(max_length=255, unique=True, null=True, blank=True)
    tong_tien = models.DecimalField(decimal_places=0, max_digits=10, null=True, blank=True)
    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)
    bao_hiem = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Hóa Đơn Thuốc"
        verbose_name_plural = "Hóa Đơn Thuốc",
        permissions = (
            ('can_checkout_medicine_receipt', 'Thanh toán hóa đơn thuốc'),
            ('can_view_medicine_receipt', 'Xem hóa đơn thuốc'),
            ('can_delete_medicine_receipt', 'Xóa hóa đơn thuốc'),
            ('can_print_medicine_receipt', 'In hóa đơn thuốc'),
            ('can_view_medicine_expense_coverage', 'Xem danh sách thuốc bảo hiểm chi trả'),
            ('can_export_medicine_expense_coverage', 'Xuất danh sách thuốc bảo hiểm chi trả'),
            ('can_view_medicine_revenue', 'Xem doanh thu thuốc'),
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonThuoc, self).save(*args, **kwargs)

    def get_don_gia(self):
        try:
            if self.tong_tien is not None:
                don_gia = "{:,}".format(int(self.tong_tien))
            else:
                don_gia = '-'
        except ValueError:
            don_gia = "{:,}".format(float(self.tong_tien))
        return don_gia

class HoaDonChuoiKham(models.Model):
    """ 
    * Bảng hóa đơn khám sẽ lưu trữ lại hóa đơn sau khi sử dụng các dịch vụ khám của tất cả người dùng 

    @field chuoi_kham: mối quan hệ 1-1 với Chuỗi Khám, vì một chuỗi khám sẽ chỉ có một hóa đơn
    @field ma_hoa_don: mã hóa đơn này sẽ do bác sĩ tự quy định, bác sĩ có thể quy định mã hóa đơn này theo người bệnh và thời gian họ khám để dễ dàng phân biệt
    @field tong_tien: tổng số tiền của các dịch vụ khám mà bệnh nhân đã khám
    @field thoi_gian_tao: thời gian hóa đơn được tạo
    @field thoi_gian_cap_nhat : thời gian hóa đơn được cập nhật
    """

    chuoi_kham = models.OneToOneField("clinic.ChuoiKham", on_delete=models.CASCADE, null=True, related_name='hoa_don_dich_vu')
    nguoi_thanh_toan = models.ForeignKey("clinic.User", on_delete=models.SET_NULL, null=True, blank=True)
    ma_hoa_don = models.CharField(max_length=255, null=True, blank=True, unique=True)
    tong_tien = models.DecimalField(decimal_places=3, max_digits=10, null=True, blank=True)
    discount = models.IntegerField(null=True, blank=True)


    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    bao_hiem = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Hóa Đơn Chuỗi Khám"
        verbose_name_plural = "Hóa Đơn Chuỗi Khám",
        permissions = (
            ('can_checkout_service_receipt', 'Thanh toán hóa đơn dịch vụ kỹ thuật'),
            ('can_view_service_receipt', 'Xem hóa đơn dịch vụ kỹ thuật'),
            ('can_delete_service_receipt', 'Xóa hóa đơn dịch vụ kỹ thuật'),
            ('can_print_service_receipt', 'In hóa đơn dịch vụ kỹ thuật'),
            ('can_view_service_expense_coverage', 'Xem danh sách dịch vụ kỹ thuật bảo hiểm chi trả'),
            ('can_export_service_expense_coverage', 'Xuất danh sách dịch vụ kỹ thuật bảo hiểm chi trả'),
            ('can_view_service_revenue', 'Xem doanh thu dịch vụ kỹ thuật'),
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonChuoiKham, self).save(*args, **kwargs)

    def get_benh_nhan(self):
        return self.chuoi_kham.benh_nhan.ho_ten

    def get_ma_benh(self):
        try:
            return self.chuoi_kham.ket_qua_tong_quat.all()[0].ma_benh.ma_benh
        except:
            return ''

    def get_tong_cong(self):
        ds_dich_vu = self.chuoi_kham.phan_khoa_kham.all()
        tong_tien = []
        for phan_khoa in ds_dich_vu:
            gia = phan_khoa.dich_vu_kham.don_gia
            tong_tien.append(gia)
        return int(sum(tong_tien))

    def get_tong_cong_2(self):
        tong_cong_2 = float(self.get_tong_cong()) - float(self.tong_tien)
        return tong_cong_2

    def get_bao_hiem_tra(self):
        ds_dich_vu = self.chuoi_kham.phan_khoa_kham.all()
        tong_tien = []
        for phan_khoa in ds_dich_vu:
            if phan_khoa.bao_hiem == True:
                gia = phan_khoa.dich_vu_kham.don_gia
                tong_tien.append(gia)
        return sum(tong_tien)

    def get_tu_chi_tra(self):
        return int(self.get_tong_cong()) - int(self.get_bao_hiem_tra())

    def get_don_gia(self):
        don_gia = "{:,}".format(int(self.tong_tien))
        return don_gia

    def get_ngay_kham(self):
        return self.thoi_gian_tao.strftime('%d-%m-%Y')

    def get_gia_xet_nghiem(self):
        return 0

    def get_gia_cdha_tdcn(self):
        return 0

    def get_gia_thuoc_1(self):
        return 0

    def get_gia_mau(self):
        return 0

    def get_gia_ttpt(self):
        return 0

    def get_gia_vtyt_1(self):
        return 0
    
    def get_gia_dvkt(self):
        return 0

    def get_gia_thuoc_2(self):
        return 0

    def get_gia_vtyt_2(self):
        return 0

    def get_gia_van_chuyen(self):
        return 0

    def get_chi_phi_ngoai_ds(self):
        return 0

class HoaDonLamSang(models.Model):
    lich_hen = models.ForeignKey("clinic.LichHenKham", on_delete=models.CASCADE, null=True, blank=True, related_name="hoa_don_lam_sang")
    nguoi_thanh_toan = models.ForeignKey("clinic.User", on_delete=models.SET_NULL, null=True, blank=True)
    tong_tien = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True)
    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Hóa Đơn Lâm Sàng"
        verbose_name_plural = "Hóa Đơn Lâm Sàng",
        permissions = (
            ('can_checkout_clinical_receipt', 'Thanh toán hóa đơn lâm sàng'),
            ('can_view_clinical_receipt', 'Xem hóa đơn lâm sàng'),
            ('can_delete_clinical_receipt', 'Xóa hóa đơn lâm sàng'),
            ('can_view_clinical_revenue', 'Xem doanh thu lâm sàng'),
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonLamSang, self).save(*args, **kwargs)

    def get_don_gia(self):
        don_gia = "{:,}".format(int(self.tong_tien))
        return don_gia

    # benh_nhan = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)

class HoaDonTong(models.Model):
    benh_nhan = models.ForeignKey("clinic.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="hoa_don_tong_nguoi_dung")
    lich_hen = models.ForeignKey("clinic.LichHenKham", on_delete=models.SET_NULL, null=True, blank=True, related_name="hoa_don_lich_hen")
    hoa_don_lam_sang = models.ForeignKey(HoaDonLamSang, on_delete=models.SET_NULL, null=True, blank=True)
    hoa_don_chuoi_kham = models.ForeignKey(HoaDonChuoiKham, on_delete=models.SET_NULL, null=True, blank=True)
    hoa_don_thuoc = models.ForeignKey(HoaDonThuoc, on_delete=models.SET_NULL, null=True, blank=True)
    bao_hiem = models.BooleanField(default=False)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonTong, self).save(*args, **kwargs)

# NEW FROM LONG
class HoaDonVatTu(models.Model):
    nguoi_phu_trach = models.ForeignKey("clinic.User", on_delete=models.SET_NULL, null=True, blank=True)
    tong_tien = models.DecimalField(max_digits=20, decimal_places=3, null=True, blank=True)
    bao_hiem = models.BooleanField(default=False)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Hóa Đơn Vật Tư Y Tế"
        verbose_name_plural = "Hóa Đơn Vật Tư Y Tế",
        permissions = (
            ('can_checkout_medical_supplies_receipt', 'Thanh toán hóa đơn vật tư y tế'),
            ('can_view_medical_supplies_receipt', 'Xem hóa đơn vật tư y tế'),
            ('can_delete_medical_supplies_receipt', 'Xóa hóa đơn vật tư y tế'),
            ('can_print_medical_supplies_receipt', 'In hóa đơn vật tư y tế'),
            ('can_view_medical_supplies_expense_coverage', 'Xem danh sách vật tư y tế bảo hiểm chi trả'),
            ('can_export_medical_supplies_expense_coverage', 'Xuất danh sách vật tư y tế bảo hiểm chi trả'),
            ('can_view_medical_supplies_revenue', 'Xem doanh thu vật tư y tế'),
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonVatTu, self).save(*args, **kwargs)

class HoaDonNhapHang(models.Model):
    nguoi_phu_trach = models.ForeignKey("clinic.User", on_delete=models.CASCADE, null=True, blank=True)
    ma_hoa_don = models.CharField(max_length=255, unique=True, blank=True, null=True)
    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Hóa Đơn Nhập Hàng"

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonNhapHang, self).save(*args, **kwargs)

class NhapHang(models.Model):
    hoa_don = models.ForeignKey(HoaDonNhapHang, on_delete=models.CASCADE, null=True, blank=True, related_name='hoa_don_nhap_hang')
    thuoc = models.ForeignKey("medicine.Thuoc", on_delete=models.CASCADE, null=True, blank=True, related_name='nhap_hang_thuoc')
    so_luong = models.PositiveIntegerField(null=True, blank=True)
    bao_hiem = models.BooleanField(default=False)

    thoi_gian_tao = models.DateTimeField(null=True, blank=True, auto_now_add = True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True, auto_now = True)

    class Meta:
        verbose_name = "Nhập Hàng"

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(NhapHang, self).save(*args, **kwargs)
        
class HoaDonXuatHang(models.Model):
    nguoi_phu_trach = models.ForeignKey("clinic.User", on_delete=models.CASCADE, null=True, blank=True)
    ma_hoa_don = models.CharField(max_length=255, unique=True, blank=True, null=True)
    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Hóa Đơn Xuất Hàng"

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonXuatHang, self).save(*args, **kwargs)

class HoaDonTonHang(models.Model):
    nguoi_phu_trach = models.ForeignKey('clinic.User', on_delete=models.CASCADE, null=True, blank=True)
    ma_hoa_don = models.CharField(max_length=255, unique=True, blank=True, null=True)
    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Hóa Đơn Tồn Hàng"

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(HoaDonTonHang, self).save(*args, **kwargs)

class TonHang(models.Model):
    hoa_don = models.ForeignKey(HoaDonTonHang, on_delete=models.CASCADE, null=True, blank=True)
    thuoc = models.ForeignKey('medicine.Thuoc', on_delete=models.CASCADE, null=True, blank=True)
    so_luong = models.PositiveIntegerField()

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)
    class Meta:
        verbose_name = "Tồn Hàng"

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(TonHang, self).save(*args, **kwargs)
# END