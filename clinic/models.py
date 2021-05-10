
import decimal
import hashlib
import datetime
import os
from bulk_update_or_create.query import BulkUpdateOrCreateQuerySet
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
from django.core.files.storage import FileSystemStorage
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import PermissionsMixin
import re
import unicodedata

def file_url(self, filename): 

    hash_ = hashlib.md5()
    hash_.update(str(filename).encode("utf-8") + str(datetime.datetime.now()).encode("utf-8"))
    file_hash = hash_.hexdigest()
    filename = filename
    return "%s%s/%s" % (self.file_prepend, file_hash, filename)

def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except (TypeError, NameError): 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)

def text_to_id(text):
    text = strip_accents(text.lower())
    text = re.sub('[ ]+', '_', text)
    text = re.sub('[^0-9a-zA-Z_-]', '', text)
    return text

class UserManager(BaseUserManager):
    def create_user(self, ho_ten, so_dien_thoai, dia_chi, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not so_dien_thoai:
            raise ValueError('Users must have an mobile number')

        if not ho_ten:
            raise ValueError('Users must have their name')

        user = self.model(
            so_dien_thoai=so_dien_thoai,
            ho_ten = ho_ten,
            dia_chi = dia_chi,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_nguoi_dung(self, ho_ten, so_dien_thoai, gioi_tinh, dan_toc, ngay_sinh, ma_so_bao_hiem, dia_chi, password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not so_dien_thoai:
            raise ValueError('Users must have an mobile number')

        if not ho_ten:
            raise ValueError('Users must have their name')

        user = self.model(
            so_dien_thoai  = so_dien_thoai,
            ho_ten         = ho_ten,
            dia_chi        = dia_chi,
            gioi_tinh      = gioi_tinh,
            dan_toc        = dan_toc,
            ngay_sinh      = ngay_sinh,
            ma_so_bao_hiem = ma_so_bao_hiem,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, ho_ten, username, so_dien_thoai, cmnd_cccd, gioi_tinh, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.model(
            username=username,
            so_dien_thoai=so_dien_thoai,
            ho_ten=ho_ten,
            cmnd_cccd = cmnd_cccd,
            gioi_tinh=gioi_tinh,
        )
        user.set_password(password)
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, ho_ten, so_dien_thoai, dia_chi, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            so_dien_thoai=so_dien_thoai,
            password=password,
            ho_ten=ho_ten,
            dia_chi = dia_chi,
        )
        
        user.staff = True
        user.admin = True
        user.superuser = True
        user.chuc_nang = 7
        user.save(using=self._db)
        return user

    def with_perm(self, perm, is_active=True, include_superusers=True, backend=None, obj=None):
        if backend is None:
            backends = auth._get_backends(return_tuples=True)
            if len(backends) == 1:
                backend, _ = backends[0]
            else:
                raise ValueError(
                    'You have multiple authentication backends configured and '
                    'therefore must provide the `backend` argument.'
                )
        elif not isinstance(backend, str):
            raise TypeError(
                'backend must be a dotted import path string (got %r).'
                % backend
            )
        else:
            backend = auth.load_backend(backend)
        if hasattr(backend, 'with_perm'):
            return backend.with_perm(
                perm,
                is_active=is_active,
                include_superusers=include_superusers,
                obj=obj,
            )
        return self.none()

class User(AbstractBaseUser, PermissionsMixin):
    file_prepend = 'user/img/'
    GENDER = (
        ('1', "Nam"),
        ('2', "Nữ"),
        ('3', "Không xác định"),
    )
    ROLE = (
        ('1', 'Người Dùng'),
        ('2', 'Lễ Tân'),
        ('3', 'Bác Sĩ Lâm Sàng'),
        ('4', 'Bác Sĩ Chuyên Khoa'),
        ('5', 'Nhân Viên Phòng Tài Chính'),
        ('6', 'Nhân Viên Phòng Thuốc'),
        ('7', 'Quản Trị Viên')
    )
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    ma_benh_nhan = models.CharField(max_length=20, unique=True, null=True)
    phone_regex = RegexValidator(regex=r"(84|0[3|5|7|8|9])+([0-9]{8})\b")
    username = models.CharField(max_length=255, unique=True, null=True, blank=True)
    so_dien_thoai = models.CharField(max_length=10, unique=True, validators=[phone_regex])
    ho_ten = models.CharField(max_length = 255)

    email = models.EmailField(null=True, blank=True)
    cmnd_cccd = models.CharField(max_length=13, null=True, unique = True)
    ngay_sinh = models.DateField(null=True, blank=True)
    gioi_tinh = models.CharField(choices=GENDER, max_length = 10, null=True, blank=True)

    can_nang = models.PositiveIntegerField(null=True, blank=True)

    anh_dai_dien = models.FileField(max_length=1000, upload_to=file_url, null=True, blank=True)
    tinh = models.ForeignKey('Province', on_delete=models.SET_NULL, null=True, blank=True)
    huyen = models.ForeignKey('District', on_delete=models.SET_NULL, null=True, blank=True)
    xa = models.ForeignKey('Ward', on_delete=models.SET_NULL, null=True, blank=True)
    dia_chi = models.TextField(max_length=1000, null=True, blank=True)
    dan_toc = models.CharField(max_length=40, null=True, blank=True)
    chuc_nang = models.CharField(choices=ROLE, max_length = 1, default='1')

    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser
    superuser = models.BooleanField(default=False)

    # notice the absence of a "Password field", that is built in.
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child')
    
    ma_so_bao_hiem = models.CharField(max_length=25, null=True, blank=True)
    ma_dkbd = models.CharField(max_length=10, null=True, blank=True)
    ma_khuvuc = models.CharField(max_length=10, null=True, blank=True)
    gt_the_tu = models.DateField(null=True, blank=True)
    gt_the_den = models.DateField(null=True, blank=True)
    mien_cung_ct = models.DateField(null=True, blank=True)
    lien_tuc_5_nam_tu = models.DateField(null=True, blank=True)

    muc_huong = models.PositiveIntegerField(null=True, blank=True)
    so_diem_tich = models.PositiveIntegerField(null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = (
            ('can_add_user', 'Thêm người dùng'),
            ('can_add_staff_user', 'Thêm nhân viên'),
            ('can_change_user_info', 'Chỉnh sửa người dùng'),
            ('can_change_staff_user_info', 'Chỉnh sửa nhân viên'),
            ('can_change_password_user', 'Thay đổi mật khẩu người dùng'),
            ('can_change_password_staff_user', 'Thay đổi mật khẩu nhân viên'),
            ('can_view_user_info', 'Xem người dùng'),
            ('can_view_staff_user_info', 'Xem nhân viên'),
            ('can_delete_user', 'Xóa người dùng'),
            ('can_delete_staff_user', 'Xóa nhân viên'),
            ('general_view', 'Xem Tổng Quan Trang Chủ'),
            ('reception_department_module_view', 'Phòng Ban Lễ Tân'),
            ('finance_department_module_view', 'Phòng Ban Tài Chính'),
            ('specialist_department_module_view', 'Phòng Ban Chuyên Gia'),
            ('preclinical_department_module_view', 'Phòng Ban Lâm Sàng'),
            ('medicine_department_module_view', 'Phòng Ban Thuốc'),
            ('general_revenue_view', 'Xem Doanh Thu Phòng Khám'),
            ('can_view_checkout_list', 'Xem Danh Sách Thanh Toán Tài Chính'),
            ('export_insurance_data', 'Xuất Bảo Hiểm Tài Chính'),
            ('can_export_list_of_patient_insurance_coverage', 'Xuất Danh Sách Bệnh Nhân Bảo Hiểm Chi Trả'),
            ('can_view_list_of_patient', 'Xem Danh Sách Bệnh Nhân Chờ'),
            ('can_bao_cao_thuoc', 'Báo Cáo Thuốc'),
            ('can_export_list_import_export_general_medicines', 'Xuất Danh Sách Xuất Nhập Tồn Tổng Hợp Thuốc'),
            ('can_export_soon_expired_list_medicines', 'Xuất Danh Sách Thuốc Sắp Hết Hạn'),
            ('can_see_general_medicine_list_report', 'Xem Báo Cáo Tổng Hợp Thuốc'),
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
            now = timezone.now()
            date_time = now.strftime("%m%d%y%H%M%S")
            self.ma_benh_nhan = date_time
        self.thoi_gian_cap_nhat = timezone.now()
        return super(User, self).save(*args, **kwargs)

    objects = UserManager()

    USERNAME_FIELD = 'so_dien_thoai'
    REQUIRED_FIELDS = ['ho_ten', 'dia_chi',] # Email & Password are required by default.

    def __str__(self):       
        return f"({self.id}) {self.ho_ten}"

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

    @property
    def is_active(self):
        "Is the user active?"
        return self.active

    @property
    def is_superuser(self):
        "Is the user active?"
        return self.superuser

    def getSubName(self):
        lstChar = []
        lstString = self.ho_ten.split(' ')
        for i in lstString:
            lstChar.append(i[0].upper())
        subName = "".join(lstChar)
        return subName

    def tuoi(self):
        now = datetime.date.today()
        if self.ngay_sinh is not None:
            days = now - self.ngay_sinh
            tuoi = int((days.days / 365))
        else:
            tuoi = 0
        return tuoi

    def get_dia_chi(self):
        if self.tinh is not None:
            tinh = self.tinh.name
        else:
            tinh = ""
        if self.huyen is not None:
            huyen = self.huyen.name
        else:
            huyen = ""
        if self.xa is not None:
            xa = self.xa.name
        else:
            xa = ""
        return f'{self.dia_chi}, {xa}, {huyen}, {tinh}'

    def get_so_dien_thoai(self):
        if self.so_dien_thoai is not None:
            return self.so_dien_thoai
        else:
            return "Không có số điện thoại"

    def get_gioi_tinh(self):
        if self.gioi_tinh == '1': 
            return "Nam"
        elif self.gioi_tinh == '2':
            return "Nữ"
        else: 
            return "Không xác định"
    
    def get_user_role(self):
        if self.chuc_nang == '2':
            return "Lễ Tân"
        elif self.chuc_nang == '3':
            return "Bác Sĩ Lâm Sàng"
        elif self.chuc_nang == '4':
            return "Bác Sĩ Chuyên Khoa"
        elif self.chuc_nang == '5':
            return "Nhân Viên Tài Chính"
        elif self.chuc_nang == '6':
            return "Nhân Viên Phòng Thuốc"
        elif self.chuc_nang == '7':
            return "Quản Trị Viên"
    
    @property
    def is_bac_si(self):
        if self.chuc_nang == '3' or self.chuc_nang == '4' or self.is_superuser:
            return True
        else:
            return False

    def get_mo_ta(self):
        if self.chuc_nang == '3' or self.chuc_nang == '4':
            mo_ta = self.user_bac_si.gioi_thieu
        else:
            mo_ta = "Nhân Viên Phòng Khám"

        return mo_ta
    
    def is_bac_si_lam_sang(self):
        if self.chuc_nang == '3' or self.is_superuser:
            return True
        else:
            return False

        
class BacSi(models.Model):
    Type = (
        ('full_time', "Full-Time"),
        ('part_time', "Part-Time"),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_bac_si')
    chung_chi_hanh_nghe = models.CharField(max_length=50, null=True, blank=True)
    gioi_thieu = models.TextField(null=True, blank=True)
    chuc_danh = models.CharField(max_length=255, null=True, blank=True)
    chuyen_khoa = models.CharField(max_length=255, null=True, blank=True)
    noi_cong_tac = models.TextField(null=True, blank=True)
    kinh_nghiem = models.TextField(null=True, blank=True)
    loai_cong_viec = models.CharField(null=True, blank=True, choices= Type, max_length=50)

    class Meta:
        verbose_name = "Bác Sĩ"
        verbose_name_plural = "Bác Sĩ"

class TinhTrangPhongKham(models.Model):
    """ Mở rộng phần tình trạng của phòng khám, khi phòng khám muốn tạm ngưng hoạt động
    trong một khoảng thời gian thì bảng này sẽ được sử dụng để mở rộng tính năng cho bảng Phòng Khám """
    kha_dung = models.BooleanField(default=True)
    thoi_gian_dong_cua = models.DateTimeField(null=True, blank=True)
    thoi_gian_mo_cua = models.DateTimeField(null=True, blank=True)

    # tọa độ địa lí của phòng khám sẽ được sử dụng để hiển thị lên map trong mobile app
    latitude = models.CharField(null=True, blank=True, max_length=50)
    longtitude = models.CharField(null=True, blank=True, max_length=50)

    ip_range_start = models.CharField(max_length=50, null=True, blank=True)
    ip_range_end = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'Tình Trạng Phòng Khám'
        verbose_name_plural = "Tình Trạng Phòng Khám"
    
class PhongKham(models.Model):
    """ Thông tin chi tiết của phòng khám """
    file_prepend = "logo_phong_kham/"

    ma_cskcb = models.CharField(max_length=10, null=True, blank=True)

    ten_phong_kham = models.CharField(max_length = 255)
    dia_chi = models.TextField(null=True, blank=True)
    so_dien_thoai = models.CharField(max_length = 12)
    email = models.EmailField(null=True, blank=True)
    logo = models.FileField(upload_to = file_url, null=True, blank=True)
    tinh_trang = models.ForeignKey(TinhTrangPhongKham, on_delete=models.CASCADE)
    gia_tri_diem_tich = models.PositiveIntegerField(null=True, blank=True)
    # NEW 
    chu_khoan = models.CharField(max_length=255, null=True, blank=True)
    so_tai_khoan = models.CharField(max_length=20, null=True, blank=True)
    thong_tin_ngan_hang = models.TextField(null=True, blank=True)
    # END
    class Meta:
        verbose_name = "Phòng Khám"
        verbose_name_plural = "Phòng Khám"
        permissions = (
            ('can_add_clinic_info', "Thêm thông tin phòng khám"),
            ('can_change_clinic_info', "Thay đổi thông tin phòng khám"),
        )

class PhongChucNang(models.Model):
    """ Mỗi dịch vụ khám sẽ có một phòng chức năng riêng biệt, là nơi bệnh nhân sau khi được phân dịch vụ khám sẽ đến trong suốt chuỗi khám của bệnh nhân """
    ten_phong_chuc_nang = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=True, blank=True)
    bac_si_phu_trach = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="bac_si_chuyen_khoa")
    # dich_vu_kham = models.ForeignKey(DichVuKham, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="phong_chuc_nang_theo_dich_vu")
    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True, auto_now_add=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True, auto_now=True)
    
    class Meta:
        verbose_name = "Phòng Chức Năng"
        verbose_name_plural = "Phòng Chức Năng"
        permissions = (
            ('can_add_consulting_room', 'Thêm phòng chức năng'),
            ('can_change_consulting_room', 'Chỉnh sửa phòng chức năng'),
            ('can_view_consulting_room', 'Xem phòng chức năng'),
            ('can_delete_consulting_room', 'Xóa phòng chức năng'),
        )

    def __str__(self):
        return self.ten_phong_chuc_nang
    
    def danh_sach_benh_nhan_theo_dich_vu_kham(self):
        # return self.dich_vu_kham.dich_vu_kham.all()
        return self.ten_phong_chuc_nang

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.slug = text_to_id(self.ten_phong_chuc_nang)
        return super(PhongChucNang, self).save(*agrs, **kwargs)

    def get_thoi_gian_tao(self):
        return self.thoi_gian_tao.strftime("%d/%m/%y %H:%M:%S")

    def get_thoi_gian_cap_nhat(self):
        return self.thoi_gian_cap_nhat.strftime("%d/%m/%y %H:%M:%S")

    # TODO review table PhongChucNang again

class DichVuKham(models.Model):
    """ Danh sách tất cả các dịch vụ khám trong phòng khám """
    khoa = models.ForeignKey("DanhMucKhoa", on_delete=models.SET_NULL, null=True, blank=True)

    ma_dvkt = models.CharField(max_length=50, null=True, blank=True)
    stt = models.CharField(max_length=10, null=True, blank=True, unique=True)
    ten_dvkt = models.CharField(max_length=255, null=True, blank=True)
    ma_gia = models.CharField(max_length=50, null=True, blank=True)
    don_gia = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=0)
    don_gia_bhyt = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=0)
    quyet_dinh = models.CharField(max_length=10, null=True, blank=True)
    cong_bo = models.CharField(max_length=10, null=True, blank=True)
    ma_cosokcb = models.CharField(max_length=20, null=True, blank=True)
    ten_dich_vu = models.CharField(max_length=255, null=True, blank=True)
    bao_hiem = models.BooleanField(default=False)

    nhom_chi_phi = models.ForeignKey('NhomChiPhi', on_delete=models.SET_NULL, null=True, blank=True)
    tyle_tt = models.IntegerField(null=True, blank=True)
    # bac_si_phu_trach = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="bac_si_phu_trach", null=True, blank=True)
    # khoa_kham = models.ForeignKey(KhoaKham, on_delete=models.SET_NULL, related_name="khoa_kham", null=True, blank=True)
    phong_chuc_nang = models.ForeignKey(PhongChucNang, on_delete=models.SET_NULL, null=True, blank=True, related_name="dich_vu_kham_theo_phong")
    
    chi_so = models.BooleanField(default=False)
    html = models.BooleanField(default=False)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    def __str__(self):
        return f'({self.id}){str(self.ten_dvkt)}'

    class Meta:
        verbose_name = "Dịch Vụ Khám"
        verbose_name_plural = "Dịch Vụ Khám"
        permissions = (
            ('can_add_service', 'Thêm dịch vụ kỹ thuật'),
            ('can_add_service_with_excel_file', 'Thêm dịch vụ kỹ thuật bằng Excel File'),
            ('can_change_service', 'Thay đổi dịch vụ kỹ thuật'),
            ('can_view_service', 'Xem dịch vụ kỹ thuật'),
            ('can_delete_service', 'Xóa dịch vụ kỹ thuật'),
            ('can_view_service_price', 'Xem giá dịch vụ kỹ thuật'),
            ('can_export_list_of_service', 'Xuất danh sách dịch vụ kỹ thuật'),
        )

    @property
    def check_chi_so(self):
        if self.chi_so == True:
            return True
        else:
            return False

    @property
    def check_html(self):
        if self.html == True:
            return True
        else:
            return False
    
    def get_don_gia(self):
        if self.don_gia is not None:
            don_gia = "{:,}".format(int(self.don_gia))
        else:
            don_gia = '-'
        return don_gia

    def get_don_gia_bhyt(self):
        if self.don_gia_bhyt is not None:
            don_gia_bhyt = "{:,}".format(int(self.don_gia_bhyt))
        else:
            don_gia_bhyt = '-'
        return don_gia_bhyt

    def get_ten_phong_chuc_nang(self):
        if self.phong_chuc_nang is not None:
            return self.phong_chuc_nang.ten_phong_chuc_nang
        else:
            return '-'
    
class GiaDichVu(models.Model):
    """ Bảng giá sẽ lưu trữ tất cả giá của dịch vụ khám và cả thuốc """
    id_dich_vu_kham = models.OneToOneField(DichVuKham, null=True, blank=True, on_delete=models.PROTECT, related_name="gia_dich_vu_kham")
    gia = models.DecimalField(max_digits=10, decimal_places=3)  
    # id_thuoc = models.ForeignKey(Thuoc, on_delete=models.PROTECT, null=True, blank=True, related_name="gia_thuoc")
    thoi_gian_tao = models.DateTimeField(null=True, blank=True, editable=False)
    thoi_gian_chinh_sua = models.DateTimeField(null=True, blank=True)

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_chinh_sua = timezone.now()
        return super(GiaDichVu, self).save(*agrs, **kwargs)

class BaoHiem(models.Model):
    """ Bảng Bảo Hiểm sẽ lưu trữ tất cả các loại bảo hiểm áp dụng trong phòng khám """
    ten_bao_hiem = models.CharField(max_length=255)
    # dạng bảo hiểm ở đây là số % được bảo hiểm chi trả
    dang_bao_hiem = models.SmallIntegerField(null=True, blank=True)
    id_dich_vu_kham = models.OneToOneField(DichVuKham, null=True, blank=True, on_delete=models.PROTECT, related_name="bao_hiem_dich_vu_kham")
    # id_thuoc = models.ForeignKey(Thuoc, on_delete=models.PROTECT, null=True, blank=True, related_name="bao_hiem_thuoc")
    thoi_gian_tao = models.DateTimeField()
    thoi_gian_chinh_sua = models.DateTimeField()

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_chinh_sua = timezone.now()
        return super(BaoHiem, self).save(*agrs, **kwargs)

class ProfilePhongChucNang(models.Model):
    phong_chuc_nang = models.OneToOneField(PhongChucNang, on_delete=models.CASCADE, related_name="profile_phong_chuc_nang")
    so_luong_cho = models.PositiveIntegerField(null=True, blank=True)
    thoi_gian_trung_binh = models.PositiveIntegerField(help_text="Đơn vị(phút)", null=True, blank=True)
    status = models.BooleanField(default=True)

@receiver(post_save, sender=PhongChucNang)
def create_or_update_func_room_profile(sender, instance, created, **kwargs):
    if created:
        ProfilePhongChucNang.objects.create(phong_chuc_nang=instance)
    instance.profile_phong_chuc_nang.save()

def get_sentinel_user():
    return User.objects.get_or_create(ho_ten='deleted')[0]

class TrangThaiLichHen(models.Model):
    ten_trang_thai = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Trạng Thái Lịch Hẹn"
        verbose_name_plural = "Trạng Thái Lịch Hẹn"

    def __str__(self):
        return f"({self.id})" + self.ten_trang_thai 

def get_default_trang_thai_lich_hen():
    return TrangThaiLichHen.objects.get_or_create(ten_trang_thai="Đã đặt trước")[0]

from datetime import timedelta

today = timezone.localtime(timezone.now())
tomorrow = today + timedelta(1)
today_start = today.replace(hour=0, minute=0, second=0)
today_end = tomorrow.replace(hour=0, minute=0, second=0)

# class LichHenKhamManager(models.Manager):
#     def lich_hen_hom_nay(self):
#         return self.filter(thoi_gian_bat_dau__lte = today_end, thoi_gian_ket_thuc__gte = today_start)
class LichHenKham(models.Model):

    LYDO_VVIEN = (
        ("1", "Đúng Tuyến"),
        ("2", "Cấp Cứu"),
        ("3", "Trái Tuyến"),
        ("4", "Thông Tuyến"),
    )

    LOAI_DICH_VU = (
        ('kham_chua_benh', 'Khám Chữa Bệnh'),
        ('kham_suc_khoe', 'Khám Sức Khỏe'),
        ('kham_theo_yeu_cau', 'Khám Theo Yêu Cầu'),
    )

    ma_lich_hen = models.CharField(max_length=15, null=True, blank=True)
    benh_nhan = models.ForeignKey(User, on_delete=models.CASCADE, related_name="benh_nhan_hen_kham")
    nguoi_phu_trach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="nguoi_phu_trach")

    thoi_gian_bat_dau = models.DateTimeField()
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)
    ly_do = models.TextField(null=True, blank=True)
    dia_diem = models.CharField(max_length=255, null=True, blank=True)
    loai_dich_vu = models.CharField(choices=LOAI_DICH_VU, null=True, blank=True, max_length=25)
    trang_thai = models.ForeignKey(TrangThaiLichHen, on_delete=models.CASCADE, null=True, blank=True)

    ly_do_vvien = models.CharField(max_length=5, choices=LYDO_VVIEN, null=True, blank=True)
    thanh_toan_sau = models.BooleanField(default = False)

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True, auto_now_add=True)
    thoi_gian_chinh_sua = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        verbose_name = "Lịch Hẹn Khám"
        verbose_name_plural = "Lịch Hẹn Khám"
        permissions = (
            ('can_add_appointment', 'Thêm lịch hẹn'),
            ('can_change_appointment', 'Thay đổi lịch hẹn'),
            ('can_view_appointment', 'Xem lịch hẹn'),
            ('can_delete_appointment', 'Xóa lịch hẹn'),
            ('can_make_reexamination', 'Thêm lịch hẹn tái khám'),
            ('can_confirm_appoinment', 'Xác nhận lịch hẹn'),
            ('can_confirm_do_examination', 'Xác nhận khám'),
        )

    def save(self, *args, **kwargs):
        if not self.id:
            now = timezone.now()
            date_time = now.strftime("%m%d%y%H%M%S")
            ma_lich_hen = "LH" + date_time
            self.ma_lich_hen = ma_lich_hen
        return super(LichHenKham, self).save(*args, **kwargs)
    
    def check_thanh_toan(self):
        hoa_don_lam_sang = self.hoa_don_lam_sang.all().last()
        if hoa_don_lam_sang is not None:
            if hoa_don_lam_sang.tong_tien is not None:
                return True
            else:
                return False
        else:
            return False

    def check_thanh_toan_sau(self):
        if self.thanh_toan_sau:
            return True
        else:
            return False

    def check_hoan_thanh_kham(self):
        hoan_thanh_kham = False
        if self.loai_dich_vu == 'kham_theo_yeu_cau':
            chuoi_kham = self.danh_sach_chuoi_kham.all().last()
            if chuoi_kham is not None:
                trang_thai_chuoi_kham = TrangThaiChuoiKham.objects.get(trang_thai_chuoi_kham='Hoàn Thành')
                if chuoi_kham.trang_thai == trang_thai_chuoi_kham:
                    hoan_thanh_kham = True

        return hoan_thanh_kham


class LichSuTrangThaiLichHen(models.Model):
    lich_hen_kham = models.ForeignKey(LichHenKham, on_delete=models.CASCADE, related_name="lich_hen")
    trang_thai_lich_hen = models.ForeignKey(TrangThaiLichHen, on_delete=models.CASCADE, related_name="trang_thai_lich_hen")
    # Nêu rõ nguyên nhân dẫn đến trạng thái đó
    chi_tiet_trang_thai = models.CharField(max_length=500, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

def get_sentinel_dich_vu():
    return DichVuKham.objects.get_or_create(ten_dich_vu='deleted')[0]

class TrangThaiKhoaKham(models.Model):
    """ Tất cả các trạng thái có thể xảy ra trong phòng khám """
    trang_thai_khoa_kham = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Trạng Thái Khoa Khám"
        verbose_name_plural = "Trạng Thái Khoa Khám"

    def __str__(self):
        return f"({self.id})" + self.trang_thai_khoa_kham 

class TrangThaiChuoiKham(models.Model):
    trang_thai_chuoi_kham = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Trạng Thái Chuỗi Khám"
        verbose_name_plural = "Trạng Thái Chuỗi Khám"

    def __str__(self):
        return f"({self.id})" + self.trang_thai_chuoi_kham

def get_default_trang_thai_chuoi_kham():
    return TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="Đang chờ")[0]

def get_default_trang_thai_khoa_kham():
    return TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham="Đang chờ")[0]

class ChuoiKham(models.Model):
    """ Mỗi bệnh nhân khi tới phòng khám để sau khi khám tổng quát thì đều sẽ có một chuỗi khám.
    Do chuỗi khám này có tính tích lũy nên bệnh nhân có thể dễ dàng xem lại được lịch sử khám của mình kết hợp với các kết quả khám tại phòng khám """
    ma_lk = models.CharField(max_length=100, null=True, blank=True)
    benh_nhan = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chuoi_kham")
    bac_si_dam_nhan = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="bac_si_chuoi_kham", null=True, blank=True)
    lich_hen = models.ForeignKey(LichHenKham, on_delete=models.CASCADE, null=True, blank=True, related_name='danh_sach_chuoi_kham')
    thoi_gian_bat_dau = models.DateTimeField(null=True, blank=True)
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)
    thoi_gian_tai_kham = models.DateTimeField(null=True, blank=True)
    trang_thai = models.ForeignKey(TrangThaiChuoiKham, on_delete=models.CASCADE, related_name="trang_thai", null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    thoi_gian_cap_nhat = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Chuỗi Khám"
        verbose_name_plural = "Chuỗi Khám"
        permissions = (
            ('can_add_assignment_chain', 'Thêm chuỗi khám'),
            ('can_change_assignment_chain', 'Thay đổi chuỗi khám'),
            ('can_view_assignment_chain', 'Xem chuỗi khám'),
            ('can_view_assignment_chain_result', 'Xem kết quả chuỗi khám'),
            ('can_delete_assignment_chain', 'Xóa chuỗi khám'),
            ('can_delete_assignment_chain_result', 'Xóa kết quả chuỗi khám'),
        )

    def get_ma_benh(self):
        return self.ket_qua_tong_quat.all()[0].ma_benh.ma_benh

    def get_ten_benh(self):
        return self.ket_qua_tong_quat.all()[0].ma_benh.ten_benh

    def get_so_ngay_dieu_tri(self):
        if (self.thoi_gian_ket_thuc - self.thoi_gian_bat_dau).days == 0:
            return "1"
        else:
            return (self.thoi_gian_ket_thuc - self.thoi_gian_bat_dau).days
    
    def get_ket_qua_dieu_tri(self):
        return self.ket_qua_tong_quat.all()[0].ket_qua_dieu_tri

    def get_ngay_ttoan(self):
        return self.hoa_don_dich_vu.thoi_gian_tao.strftime("%Y%m%d%H%M")
    
    def get_tien_thuoc(self):
        return self.don_thuoc_chuoi_kham.all()[0].hoa_don_thuoc.tong_tien

    def get_nam_qt(self):
        return self.hoa_don_dich_vu.thoi_gian_tao.strftime("%Y")

    def get_thang_qt(self):
        return self.hoa_don_dich_vu.thoi_gian_tao.strftime("%m")

    def get_ma_loai_kcb(self):
        return '1'

    def get_ma_pttt_qt(self):
        return ""

    def get_chi_phi_dich_vu(self):
        
        if (hasattr(self, 'hoa_don_dich_vu')):
            if self.hoa_don_dich_vu.tong_tien is not None:
                tong_tien = "{:,}".format(int(self.hoa_don_dich_vu.tong_tien))
            else:
                tong_tien = "-"
        else:
            tong_tien = '-'

        return tong_tien
    
    def get_chi_phi_lam_sang(self):
        lich_hen = self.lich_hen
        if lich_hen is not None:
            hoa_don_lam_sang = self.lich_hen.hoa_don_lam_sang.all().first()
            if hoa_don_lam_sang is not None:
                tong_tien = "{:,}".format(int(hoa_don_lam_sang.tong_tien))
            else:
                tong_tien = '-'
            return tong_tien
        else: 
            return '-'

    def get_chi_phi_thuoc(self):
        don_thuoc = self.don_thuoc_chuoi_kham.all().first()
        if don_thuoc is not None:
            if (hasattr(don_thuoc, 'hoa_don_thuoc')):
                hoa_don_thuoc = don_thuoc.hoa_don_thuoc
                if hoa_don_thuoc.tong_tien is not None:
                    tong_tien = "{:,}".format(int(hoa_don_thuoc.tong_tien))
                else:
                    tong_tien = '-'
            else:
                tong_tien = '-'
        else:
            tong_tien = '-'
        return tong_tien


    @property
    def check_don_thuoc_exist(self):
        don_thuoc = self.don_thuoc_chuoi_kham.all().first()
        if don_thuoc is not None:
            return True
        else:
            return False

    def get_id_don_thuoc(self):
        don_thuoc = self.don_thuoc_chuoi_kham.all().first()
        id_don_thuoc = don_thuoc.id 
        return id_don_thuoc

    def check_da_thanh_toan(self):
        da_thanh_toan = TrangThaiChuoiKham.objects.filter(trang_thai_chuoi_kham='Đã Thanh Toán').first()
        if self.trang_thai == da_thanh_toan:
            return True
        else:
            return False

    def check_thanh_toan(self):
        hoa_don_dich_vu = self.hoa_don_dich_vu
        if hoa_don_dich_vu is not None:
            if hoa_don_dich_vu.tong_tien is not None:
                return True
            else:
                return False
        else:
            return False

class PhanKhoaKham(models.Model):
    benh_nhan = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    dich_vu_kham = models.ForeignKey(DichVuKham, on_delete=models.SET_NULL, null=True, blank=True, related_name="phan_khoa_dich_vu")
    bac_si_lam_sang = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="bac_si", null=True)
    chuoi_kham = models.ForeignKey(ChuoiKham, on_delete=models.CASCADE, null=True, blank=True, related_name="phan_khoa_kham")
    bao_hiem = models.BooleanField(default=False)

    priority = models.SmallIntegerField(null=True, blank=True)

    thoi_gian_bat_dau = models.DateTimeField(null=True, blank=True)
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)

    trang_thai = models.ForeignKey(TrangThaiKhoaKham, on_delete=models.SET_NULL, null=True)

    thoi_gian_tao = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True, auto_now=True)

    class Meta:
        verbose_name = "Phân Khoa Khám"
        verbose_name_plural = "Phân Khoa Khám"
        permissions = (
            ('can_add_service_assignment', 'Thêm phân khoa khám'),
            ('can_view_service_assignment', 'Xem phân khoa khám'),
            ('can_delete_service_assignment', 'Xóa phân khoa khám'),
            ('can_do_specialist_examination', 'Có thể khám chuyên khoa'),
            ('can_stop_serivce_assignment', 'Dừng khám'),
        )

    def get_ten_benh_nhan(self):
        if self.benh_nhan is not None:
            return self.benh_nhan.ho_ten
        else:
            return "Không xác định"

    def get_dich_vu_gia(self):
        if not self.bao_hiem:
            if self.dich_vu_kham.don_gia is not None:
                don_gia = self.dich_vu_kham.don_gia
                return "{:,}".format(int(don_gia))
            else:
                return 0
        else:
            if self.dich_vu_kham.don_gia_bhyt is not None:
                don_gia = self.dich_vu_kham.don_gia_bhyt
                return "{:,}".format(int(don_gia))
            else:
                return 0

    def get_dia_chi_benh_nhan(self):
        if self.benh_nhan is not None:
            if self.benh_nhan.tinh is not None:
                province = self.benh_nhan.tinh.name
            else:
                province = "-"

            if self.benh_nhan.huyen is not None:
                district = self.benh_nhan.huyen.name
            else:
                district = "-"

            if self.benh_nhan.xa is not None:
                ward = self.benh_nhan.xa.name
            else:
                ward = "-"
            return f"{self.benh_nhan.dia_chi}, {ward}, {district}, {province}"
        else:
            return "Không có địa chỉ"

    def get_tuoi_benh_nhan(self):
        if self.benh_nhan is not None:
            return self.benh_nhan.tuoi()
        else:
            return "-"
    
    def get_gioi_tinh_benh_nhan(self):
        if self.benh_nhan is not None:
            if self.benh_nhan.gioi_tinh == '1':
                return "Nam"
            elif self.benh_nhan.gioi_tinh == '2':
                return "Nữ"
            else:
                return "Không xác định"
        else:
            return "Không xác định"

    def get_bac_si_chi_dinh(self):
        if self.bac_si_lam_sang is not None:
            return self.bac_si_lam_sang.ho_ten
        else:
            return "Không có"
        
    def gia_dich_vu_theo_bao_hiem(self):
        gia = self.dich_vu_kham.gia_dich_vu_kham.gia 
        if self.bao_hiem:
            tong_tien = gia * decimal.Decimal((1 - (self.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem / 100)))
        else:
            tong_tien = gia
        return tong_tien

    def gia(self):
        return self.dich_vu_kham.gia_dich_vu_kham.gia 

    def muc_bao_hiem(self):
        return self.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem

    def get_ma_vat_tu(self):
        return ""

    def get_so_luong(self):
        return '1'

    def get_ngay_yl(self):
        return self.thoi_gian_bat_dau.strftime("%Y%m%d%H%M")

    def get_ngay_kq(self):
        return self.thoi_gian_ket_thuc.strftime("%Y%m%d%H%M")

    def get_t_nguonkhac(self):
        return 0
    
    def get_t_ngoaids(self):
        return 0

    def get_ma_pttt(self):
        return 1

    @property
    def check_bao_hiem(self):
        if self.bao_hiem == True:
            return True
        else:
            return False
    
@receiver(post_save, sender=PhanKhoaKham)
def send_func_room_info(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"funcroom_service", {
                'type': 'funcroom_info'
            }
        )

class LichSuTrangThaiKhoaKham(models.Model):
    phan_khoa_kham = models.ForeignKey(PhanKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    trang_thai_khoa_kham = models.ForeignKey(TrangThaiKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    # Nêu rõ nguyên nhân dẫn tới trạng thái đó
    chi_tiet_trang_thai = models.CharField(max_length=500, null=True, blank=True)
    
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

class LichSuChuoiKham(models.Model):
    chuoi_kham = models.ForeignKey(ChuoiKham, on_delete=models.CASCADE, null=True, blank=True)
    trang_thai = models.ForeignKey(TrangThaiChuoiKham, on_delete=models.CASCADE, null=True, blank=True)
    # Nêu rõ nguyên nhân dẫn tới trạng thái đó
    chi_tiet_trang_thai = models.CharField(max_length=500, null=True, blank=True)
    
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

class KetQuaTongQuat(models.Model):
    """ Kết quả tổng quát của người dùng sau một lần đến thăm khám tại phòng khám """

    RESULT_CHOICES = (
        ("1", "Khỏi"),
        ("2", "Đỡ"), 
        ("3", "Không Thay Đổi"),
        ("4", "Nặng Hơn"),
        ("5", "Tử Vong"),
    )

    chuoi_kham = models.ForeignKey(ChuoiKham, on_delete=models.SET_NULL, null=True, related_name="ket_qua_tong_quat")
    # benh_nhan = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    ma_benh = models.ForeignKey('DanhMucBenh', on_delete=models.SET_NULL, null=True, blank=True)
    ma_ket_qua = models.CharField(max_length=50, null=True, blank=True)
    mo_ta = models.CharField(max_length=255, null=True, blank=True)
    ket_luan = models.TextField(null=True, blank=True)

    ket_qua_dieu_tri = models.CharField(max_length=5, choices=RESULT_CHOICES, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Kết Quả Tổng Quát"
        verbose_name_plural = "Kết Quả Tổng Quát"
        permissions = (
            ('can_add_general_result', 'Thêm kết quả tổng quát'),
            ('can_view_general_result', 'Xem kết quả tổng quát'),
            ('can_change_general_result', 'Thay đổi kết quả tổng quát'),
            ('can_delete_general_result', 'Xóa kết quả tổng quát'),
        )

    def get_mo_ta(self):
        if not self.mo_ta:
            return "Không có mô tả"
        return self.mo_ta
    
    def get_ket_luan(self):
        if not self.ket_luan:
            return "Không có kết luận"
        return self.ket_luan

    @property
    def check_html_ket_qua(self):
        if self.html_ket_qua_tong_quat.exists():
            return True
        else:
            return False

class KetQuaChuyenKhoa(models.Model):
    """ Kết quả của khám chuyên khoa mà người dùng có thể nhận được """ 
    ma_ket_qua = models.CharField(max_length=50, null=True, blank=True, unique=True)
    bac_si_chuyen_khoa = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ket_qua_bac_si_chuyen_khoa')
    phan_khoa_kham = models.ForeignKey(PhanKhoaKham, on_delete=models.CASCADE, null=True, blank=True, related_name="ket_qua_chuyen_khoa")
    ket_qua_tong_quat = models.ForeignKey(KetQuaTongQuat, on_delete=models.CASCADE, related_name="ket_qua_chuyen_khoa")
    mo_ta = models.CharField(max_length=255, null=True, blank=True)
    ket_luan = models.TextField(null=True, blank=True)

    chi_so = models.BooleanField(default = False)
    html = models.BooleanField(default=False)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Kết Quả Chuyên Khoa"
        verbose_name_plural = "Kết Quả Chuyên Khoa"
        permissions = (
            ('can_add_specialty_result', 'Thêm kết quả chuyên khoa'),
            ('can_view_specialty_result', 'Xem kết quả chuyên khoa'),
            ('can_change_specialty_result', 'Thay đổi kết quả chuyên khoa'),
            ('can_delete_specialty_result', 'Xóa kết quả chuyên khoa'),
            ('can_view_history_specialty_result', 'Xem lịch sử khám chuyên khoa'),
        )

    def get_mo_ta(self):
        if not self.mo_ta:
            return "Không có mô tả"
        return self.mo_ta
    
    def get_ket_luan(self):
        if not self.ket_luan:
            return "Không có kết luận"
        return self.ket_luan

    def get_ten_dich_vu(self):
        if self.phan_khoa_kham is not None:
            if self.phan_khoa_kham.dich_vu_kham is not None:
                return self.phan_khoa_kham.dich_vu_kham.ten_dvkt
            else:
                return "Không xác định"
        else:
            return "Không xác định"

key_store = FileSystemStorage()

class FileKetQua(models.Model):
    """ File kết quả của mỗi người dùng """
    file_prepend = 'user/documents/'
    file = models.FileField(upload_to=file_url,null=True, blank=True, storage=key_store)
    # file = models.CharField(max_length=500, null=True, blank=True)
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tài Liệu"
        verbose_name_plural = "Tài Liệu"
    
    def __unicode__(self):
        return self.file.url

    def filename(self):
        return os.path.basename(self.file.name)
    
    def get_url(self):
        return self.file.url
    # ket_qua_chuyen_khoa = models.ForeignKey(KetQuaChuyenKhoa, on_delete=models.SET_NULL, null=True, blank=True, related_name="file_ket_qua_chuyen_khoa")
    # ket_qua_tong_quat = models.ForeignKey(KetQuaTongQuat, on_delete=models.SET_NULL, null=True, blank=True, related_name="file_ket_qua_tong_quat")

class FileKetQuaTongQuat(models.Model):
    file = models.ForeignKey(FileKetQua, on_delete=models.CASCADE, related_name="file_tong_quat")
    ket_qua_tong_quat = models.ForeignKey(KetQuaTongQuat, on_delete=models.CASCADE, related_name="file_ket_qua_tong_quat")

    class Meta:
        verbose_name = "File Kết Quả Tổng Quát"
        verbose_name_plural = "File Kết Quả Tổng Quát"

class FilePhongKham(models.Model):
    file_prepend = 'phongkham/documents/'
    file = models.FileField(upload_to=file_url, null=True, blank=True, storage=key_store)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Tài Liệu Phòng Khám"
        verbose_name_plural = "Tài Liệu Phòng Khám"

class FileKetQuaChuyenKhoa(models.Model):
    file = models.ForeignKey(FileKetQua, on_delete=models.CASCADE, related_name="file_chuyen_khoa")
    ket_qua_chuyen_khoa = models.ForeignKey(KetQuaChuyenKhoa, on_delete=models.CASCADE, related_name="file_ket_qua_chuyen_khoa")

    class Meta:
        verbose_name = "File Kết Quả Chuyên Khoa"
        verbose_name_plural = "File Kết Quả Chuyên Khoa"

class BaiDang(models.Model):
    file_prepend = 'bai_dang/'
    tieu_de = models.CharField(null=True, blank=True, max_length=1024)
    hinh_anh = models.ImageField(upload_to = file_url, null=True, blank=True)
    noi_dung_chinh = models.TextField(null=True, blank=True)
    noi_dung = models.TextField(null=True, blank=True)
    thoi_gian_bat_dau = models.DateTimeField(null=True, blank=True)
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)
    nguoi_dang_bai = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="nguoi_dang_bai", null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "Bài Đăng"
        verbose_name_plural = "Bài Đăng"
        permissions = (
            ('can_add_news', 'Thêm bài đăng'),
            ('can_change_news', 'Thay đổi bài đăng'),
            ('can_view_news', 'Xem bài đăng'),
            ('can_delete_news', 'Xóa bài đăng'),
        )

    def get_truncated_noi_dung_chinh(self):
        noi_dung_chinh = (self.noi_dung_chinh[:75] + '...') if len(self.noi_dung_chinh) > 75 else self.noi_dung_chinh
        return noi_dung_chinh

# * ------ Update 19/01 -------

class NhomChiSoXetNghiem(models.Model):
    ten_nhom = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Nhóm Chỉ Số Xét Nghiệm"
        verbose_name_plural = "Nhóm Chỉ Số Xét Nghiệm"

    def __str__(self):
        return f"({self.id}){self.ten_nhom}"

class ChiSoXetNghiem(models.Model):
    dich_vu_kham = models.ForeignKey(DichVuKham, on_delete=models.CASCADE, null=True, blank=True, related_name="chi_so_xet_nghiem")
    doi_tuong_xet_nghiem = models.ForeignKey("DoiTuongXetNghiem", on_delete=models.SET_NULL, null=True, blank=True)
    nhom_chi_so = models.ForeignKey("NhomChiSoXetNghiem", on_delete=models.CASCADE, null=True, blank=True)
    ma_chi_so = models.CharField(max_length=10, null=True, blank=True)
    ten_chi_so = models.CharField(max_length=255, null=True, blank=True)
    chi_tiet = models.ForeignKey("ChiTietChiSoXetNghiem", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Chỉ Số Xét Nghiệm"
        verbose_name_plural = "Chỉ Số Xét Nghiệm"
        permissions = (
            ('can_add_test_values', 'Thêm chỉ số xét nghiệm'),
            ('can_change_test_values', 'Thay đổi chỉ số xét nghiệm'),
            ('can_view_test_values', 'Xem chỉ số xét nghiệm'),
            ('can_delete_test_values', 'Xóa chỉ số xét nghiệm'),
        )

    def __str__(self):
        return f"({self.ma_chi_so}){self.ten_chi_so}/{self.doi_tuong_xet_nghiem}"

class ChiTietChiSoXetNghiem(models.Model):
    chi_so_binh_thuong_min = models.CharField(null=True, blank=True, max_length=10)
    chi_so_binh_thuong_max = models.CharField(null=True, blank=True, max_length=10)
    chi_so_binh_thuong = models.CharField(null=True, blank=True, max_length=10)
    don_vi_do = models.CharField(max_length=50, null=True, blank=True)
    ghi_chu = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Chi Tiết Chỉ Số Xét Nghiệm"
        verbose_name_plural = "Chi Tiết Chỉ Số Xét Nghiệm"

    def __str__(self):
        if not self.chi_so_binh_thuong:
            return f"({self.chi_so_binh_thuong_min}-{self.chi_so_binh_thuong_max})-{self.ghi_chu}"
        elif not self.chi_so_binh_thuong_min and self.chi_so_binh_thuong_max:
            return f"{self.chi_so_binh_thuong}"

    @property
    def check_chi_so_binh_thuong(self):
        if not self.chi_so_binh_thuong:
            return False
        else:
            return True

    def get_chi_so_binh_thuong_min(self):
        if not self.chi_so_binh_thuong_min:
            return ""
        else:
            return self.chi_so_binh_thuong_min

    def get_chi_so_binh_thuong_max(self):
        if not self.chi_so_binh_thuong_max:
            return ""
        else:
            return self.chi_so_binh_thuong_max
    
    def get_chi_so_binh_thuong(self):
        if not self.chi_so_binh_thuong:
            return ""
        else:
            return self.chi_so_binh_thuong
    
    def get_don_vi_do(self):
        if not self.don_vi_do:
            return ""
        else:
            return self.don_vi_do

    def get_ghi_chu(self):
        if not self.ghi_chu:
            return ""
        else:
            return self.ghi_chu

class DoiTuongXetNghiem(models.Model):
    MALE = "1"
    FEMALE = "2"
    UNDEFINED = "3"
    gender_choices = (
        (MALE, "Nam"),
        (FEMALE, "Nữ"),
        (UNDEFINED, "Chưa Xác Định"),
    )
    gioi_tinh = models.CharField(choices=gender_choices, max_length=5, null=True, blank=True)
    do_tuoi = models.ForeignKey('DoTuoiXetNghiem', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Đối Tượng Xét Nghiệm"
        verbose_name_plural = "Đối Tượng Xét Nghiệm"

    def __str__(self):
        if self.gioi_tinh == "1":        
            return f"Nam({self.do_tuoi})"
        elif self.gioi_tinh == "2":
            return f"Nữ({self.do_tuoi})"
        else:
            return f"Không Xác Định({self.do_tuoi})"
    
class DoTuoiXetNghiem(models.Model):
    do_tuoi_min = models.PositiveIntegerField(null=True, blank=True)
    do_tuoi_max = models.PositiveIntegerField(null=True, blank=True)
    ghi_chu = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Độ Tuổi Xét Nghiệm"
        verbose_name_plural = "Độ Tuổi Xét Nghiệm"

    def __str__(self):
        if not self.do_tuoi_min:
            return "< " + str(self.do_tuoi_max)
        elif not self.do_tuoi_max:
            return "> " + str(self.do_tuoi_min)
        else:
            return str(self.do_tuoi_min) + "-" + str(self.do_tuoi_max)

class KetQuaXetNghiem(models.Model):
    OK = "1"
    NG = "0"
    judment_choices = (
        (OK, "Bình thường"),
        (NG, "Bất bình thường"),
    )
    phan_khoa_kham = models.ForeignKey(PhanKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    ket_qua_chuyen_khoa = models.ForeignKey(KetQuaChuyenKhoa, on_delete=models.CASCADE, null=True, blank=True, related_name="ket_qua_xet_nghiem")
    chi_so_xet_nghiem = models.ForeignKey(ChiSoXetNghiem, on_delete=models.SET_NULL, null=True, blank=True)
    ket_qua_xet_nghiem = models.CharField(max_length=50, null=True, blank=True)
    danh_gia_chi_so = models.CharField(choices=judment_choices, max_length=5, null=True, blank=True)
    danh_gia_ghi_chu = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Kết Quả Xét Nghiệm"
        verbose_name_plural = "Kết Quả Xét Nghiệm"
        permissions = (
            ('can_add_lab_result', 'Thêm kết quả xét nghiệm'),
            ('can_change_lab_result', 'Thay đổi kết quả xét nghiệm'),
            ('can_view_lab_result', 'Xem kết quả xét nghiệm'),
            ('can_delete_lab_result', 'Xóa kết quả xét nghiệm'),
        )

    def get_ten_chi_so(self):
        if self.chi_so_xet_nghiem is not None:
            return self.chi_so_xet_nghiem.ten_chi_so
        else:
            return "Không xác định"

    def get_chi_so_min(self):
        if self.chi_so_xet_nghiem is not None:
            if self.chi_so_xet_nghiem.chi_tiet is not None:
                return self.chi_so_xet_nghiem.chi_tiet.chi_so_binh_thuong_min
            else:
                return 0
        else:
            return "Không xác định"

    def get_chi_so_max(self):
        if self.chi_so_xet_nghiem is not None:
            if self.chi_so_xet_nghiem.chi_tiet is not None:
                return self.chi_so_xet_nghiem.chi_tiet.chi_so_binh_thuong_max
            else:
                return 0
        else:
            return "Không xác định"

    def get_don_vi(self):
        if self.chi_so_xet_nghiem is not None:
            if self.chi_so_xet_nghiem.chi_tiet is not None:
                if self.chi_so_xet_nghiem.chi_tiet.don_vi_do is not None:
                    return self.chi_so_xet_nghiem.chi_tiet.don_vi_do
                else:
                    return ""
            else:
                return ""
        else:
            return ""

    def get_ket_qua_xet_nghiem(self):
        if not self.ket_qua_xet_nghiem:
            return "Không có"
        else:
            return self.ket_qua_xet_nghiem

    def get_ten_dvkt(self):
        return self.phan_khoa_kham.dich_vu_kham.ten_dvkt

class HtmlKetQua(models.Model):
    phan_khoa_kham = models.ForeignKey(PhanKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    ket_qua_tong_quat = models.ForeignKey(KetQuaTongQuat, on_delete=models.CASCADE, null=True, blank=True, related_name="html_ket_qua_tong_quat")
    ket_qua_chuyen_khoa = models.ForeignKey(KetQuaChuyenKhoa, on_delete=models.CASCADE, null=True, blank=True, related_name="html_ket_qua")
    noi_dung = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "Kết Quả Dạng HTML"
        verbose_name_plural = "Kết Quả Dạng HTML"

class DanhMucChuongBenh(models.Model):
    stt = models.CharField(max_length=5, null=True, blank=True)
    ma_chuong = models.CharField(max_length=15, null=True, blank=True)
    ten_chuong = models.CharField(max_length=255, null=True, blank=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Danh Mục Chương Bệnh"
        verbose_name_plural = "Danh Mục Chương Bệnh" 

    def __str__(self):
        return self.stt + f" ({self.ma_chuong})"

class DanhMucNhomBenh(models.Model):
    chuong_benh = models.ForeignKey(DanhMucChuongBenh, on_delete=models.CASCADE, null=True, blank=True, related_name="nhom_benh")
    ma_nhom_chinh = models.CharField(max_length=15, null=True, blank=True)
    ten_nhom_chinh = models.CharField(max_length=255, null=True, blank=True)
    ma_nhom_phu_1 = models.CharField(max_length=15, null=True, blank=True)
    ten_nhom_phu_1 = models.CharField(max_length=255, null=True, blank=True)
    ma_nhom_phu_2 = models.CharField(max_length=15, null=True, blank=True)
    ten_nhom_phu_2 = models.CharField(max_length=255, null=True, blank=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Danh Mục Nhóm Bệnh"
        verbose_name_plural = "Danh Mục Nhóm Bệnh"

    def __str__(self):
        return self.ten_nhom_chinh

class DanhMucLoaiBenh(models.Model):
    nhom_benh = models.ForeignKey(DanhMucNhomBenh, on_delete=models.CASCADE, null=True, blank=True, related_name="loai_benh")
    ma_loai = models.CharField(max_length=10, null=True, blank=True)
    ten_loai = models.CharField(max_length=255, null=True, blank=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Danh Mục Loại Bệnh"
        verbose_name_plural = "Danh Mục Loại Bệnh"
    
    def __str__(self):
        return self.ten_loai

class DanhMucBenh(models.Model):
    loai_benh = models.ForeignKey(DanhMucLoaiBenh, on_delete=models.CASCADE, null=True, blank=True, related_name="benh")
    ma_benh = models.CharField(max_length=15, null=True, blank=True)
    ten_benh = models.CharField(max_length=1024, null=True, blank=True)
    ma_nhom_bcao_byt = models.CharField(max_length=5, null=True, blank=True)
    ma_nhom_chi_tiet = models.CharField(max_length=10, null=True, blank=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Danh Mục Bệnh"
        verbose_name_plural = "Danh Mục Bệnh"

    def __str__(self):
        return self.ten_benh

class NhomChiPhi(models.Model):
    ma_nhom = models.CharField(max_length=2, null=True, blank=True)
    ten_nhom = models.CharField(max_length=255, null=True, blank=True)
    ghi_chu = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Nhóm Chi Phí"
        verbose_name_plural = "Nhóm Chi Phí"

    def __str__(self):
        return f"({self.ma_nhom}) {self.ten_nhom}"

class NhomTaiNan(models.Model):
    ma_nhom = models.CharField(max_length=2, null=True, blank=True)
    ten_nhom = models.CharField(max_length=100, null=True, blank=True)
    ghi_chu = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Nhóm Tai Nạn"
        verbose_name_plural = "Nhóm Tai Nạn"
    def __str__(self):
        return self.ten_nhom

class DanhMucKhoa(models.Model):
    stt = models.IntegerField(null=True, blank=True)
    ma_khoa = models.CharField(max_length=5, null=True, blank=True)
    ten_khoa = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Danh Mục Khoa"
        verbose_name_plural = "Danh Mục Khoa"

    def __str__(self):
        return self.ten_khoa

class ThietBi(models.Model):
    ma_may = models.CharField(max_length=50, null=True, blank=True)
    ten_may = models.CharField(max_length=255, null=True, blank=True)
    ghi_chu = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Thiết Bị"
        verbose_name_plural = "Thiết Bị"

    def __str__(self):
        return self.ten_may

class GoiThau(models.Model):
    ma_goi = models.CharField(max_length=5, null=True, blank=True)
    goi = models.CharField(max_length=255, null=True, blank=True)
    nhom = models.CharField(max_length=255, null=True, blank=True)
    ma_nhom = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = "Gói Thầu"
        verbose_name_plural = "Gói Thầu"

class DuongDungThuoc(models.Model):
    stt = models.IntegerField(null=True, blank=True)
    ma_duong_dung = models.CharField(max_length=5, null=True, blank=True)
    ten_duong_dung = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Đường Dùng Thuốc"
        verbose_name_plural = "Đường Dùng Thuốc"

class MauPhieu(models.Model):
    dich_vu = models.ForeignKey(DichVuKham, on_delete=models.SET_NULL, null=True, blank=True, related_name="mau_phieu")
    ten_mau = models.CharField(max_length=255, null=True, blank=True)
    codename = models.CharField(max_length=255, null=True, blank=True, unique=True)
    noi_dung = models.TextField()

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.ten_mau

    class Meta:
        verbose_name = "Mẫu Phiếu"
        verbose_name_plural = "Mẫu Phiếu"
        permissions = (
            ('can_add_analysis_note', 'Thêm mẫu phiếu'),
            ('can_change_analysis_note', 'Thay đổi mẫu phiếu'),
            ('can_view_analysis_note', 'Xem mẫu phiếu'),
            ('can_delete_analysis_note', 'Xóa mẫu phiếu'),
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_cap_nhat = timezone.now()
        return super(MauPhieu, self).save(*args, **kwargs)

class Province(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

class District(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="district")
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name

class Ward(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="ward")
    name = models.CharField(max_length=255, null=True, blank=True)  
    type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
