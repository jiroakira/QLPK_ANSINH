
from finance.models import HoaDonChuoiKham
from django.db.models import CharField
from datetime import timedelta
from django.db.models.functions import Lower
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
from django.db.models import Count, F, Sum, Q
from finance.models import HoaDonChuoiKham


def file_url(self, filename):

    hash_ = hashlib.md5()
    hash_.update(str(filename).encode("utf-8") +
                 str(datetime.datetime.now()).encode("utf-8"))
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
            ho_ten=ho_ten,
            dia_chi=dia_chi,
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
            so_dien_thoai=so_dien_thoai,
            ho_ten=ho_ten,
            dia_chi=dia_chi,
            gioi_tinh=gioi_tinh,
            dan_toc=dan_toc,
            ngay_sinh=ngay_sinh,
            ma_so_bao_hiem=ma_so_bao_hiem,
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
            cmnd_cccd=cmnd_cccd,
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
            dia_chi=dia_chi,
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
        ('2', "N???"),
        ('3', "Kh??ng x??c ?????nh"),
    )
    ROLE = (
        ('1', 'Ng?????i D??ng'),
        ('2', 'L??? T??n'),
        ('3', 'B??c S?? L??m S??ng'),
        ('4', 'B??c S?? Chuy??n Khoa'),
        ('5', 'Nh??n Vi??n Ph??ng T??i Ch??nh'),
        ('6', 'Nh??n Vi??n Ph??ng Thu???c'),
        ('7', 'Qu???n Tr??? Vi??n')
    )
    id = models.AutoField(auto_created=True, primary_key=True,
                          serialize=False, verbose_name='ID')
    ma_benh_nhan = models.CharField(max_length=20, unique=True, null=True)
    phone_regex = RegexValidator(regex=r"(84|0[3|5|7|8|9])+([0-9]{8})\b")
    username = models.CharField(
        max_length=255, unique=True, null=True, blank=True)
    so_dien_thoai = models.CharField(
        max_length=10, unique=True, validators=[phone_regex])
    ho_ten = models.CharField(max_length=255)

    email = models.EmailField(null=True, blank=True)
    cmnd_cccd = models.CharField(max_length=13, null=True, unique=True)
    ngay_sinh = models.DateField(null=True, blank=True)
    gioi_tinh = models.CharField(
        choices=GENDER, max_length=10, null=True, blank=True)

    can_nang = models.PositiveIntegerField(null=True, blank=True)

    anh_dai_dien = models.FileField(
        max_length=1000, upload_to=file_url, null=True, blank=True)
    tinh = models.ForeignKey(
        'Province', on_delete=models.SET_NULL, null=True, blank=True)
    huyen = models.ForeignKey(
        'District', on_delete=models.SET_NULL, null=True, blank=True)
    xa = models.ForeignKey(
        'Ward', on_delete=models.SET_NULL, null=True, blank=True)
    dia_chi = models.TextField(max_length=1000, null=True, blank=True)
    dan_toc = models.CharField(max_length=40, null=True, blank=True)
    chuc_nang = models.CharField(choices=ROLE, max_length=1, default='1')

    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)  # a admin user; non super-user
    admin = models.BooleanField(default=False)  # a superuser
    superuser = models.BooleanField(default=False)

    # notice the absence of a "Password field", that is built in.
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child')

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
            ('can_add_user', 'Th??m ng?????i d??ng'),
            ('can_add_staff_user', 'Th??m nh??n vi??n'),
            ('can_change_user_info', 'Ch???nh s???a ng?????i d??ng'),
            ('can_change_staff_user_info', 'Ch???nh s???a nh??n vi??n'),
            ('can_change_password_user', 'Thay ?????i m???t kh???u ng?????i d??ng'),
            ('can_change_password_staff_user', 'Thay ?????i m???t kh???u nh??n vi??n'),
            ('can_view_user_info', 'Xem ng?????i d??ng'),
            ('can_view_staff_user_info', 'Xem nh??n vi??n'),
            ('can_delete_user', 'X??a ng?????i d??ng'),
            ('can_delete_staff_user', 'X??a nh??n vi??n'),
            ('general_view', 'Xem T???ng Quan Trang Ch???'),
            ('reception_department_module_view', 'Ph??ng Ban L??? T??n'),
            ('finance_department_module_view', 'Ph??ng Ban T??i Ch??nh'),
            ('specialist_department_module_view', 'Ph??ng Ban Chuy??n Gia'),
            ('preclinical_department_module_view', 'Ph??ng Ban L??m S??ng'),
            ('medicine_department_module_view', 'Ph??ng Ban Thu???c'),
            ('general_revenue_view', 'Xem Doanh Thu Ph??ng Kh??m'),
            ('can_view_checkout_list', 'Xem Danh S??ch Thanh To??n T??i Ch??nh'),
            ('export_insurance_data', 'Xu???t B???o Hi???m T??i Ch??nh'),
            ('can_export_list_of_patient_insurance_coverage',
             'Xu???t Danh S??ch B???nh Nh??n B???o Hi???m Chi Tr???'),
            ('can_view_list_of_patient', 'Xem Danh S??ch B???nh Nh??n Ch???'),
            ('can_bao_cao_thuoc', 'B??o C??o Thu???c'),
            ('can_export_list_import_export_general_medicines',
             'Xu???t Danh S??ch Xu???t Nh???p T???n T???ng H???p Thu???c'),
            ('can_export_soon_expired_list_medicines',
             'Xu???t Danh S??ch Thu???c S???p H???t H???n'),
            ('can_see_general_medicine_list_report', 'Xem B??o C??o T???ng H???p Thu???c'),
            ('can_view_general_features', "Ph??ng T???ng H???p"),
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
    # Email & Password are required by default.
    REQUIRED_FIELDS = ['ho_ten', 'dia_chi', ]

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
            return "Kh??ng c?? s??? ??i???n tho???i"

    def get_gioi_tinh(self):
        if self.gioi_tinh == '1':
            return "Nam"
        elif self.gioi_tinh == '2':
            return "N???"
        else:
            return "Kh??ng x??c ?????nh"

    def get_user_role(self):
        if self.chuc_nang == '2':
            return "L??? T??n"
        elif self.chuc_nang == '3':
            return "B??c S?? L??m S??ng"
        elif self.chuc_nang == '4':
            return "B??c S?? Chuy??n Khoa"
        elif self.chuc_nang == '5':
            return "Nh??n Vi??n T??i Ch??nh"
        elif self.chuc_nang == '6':
            return "Nh??n Vi??n Ph??ng Thu???c"
        elif self.chuc_nang == '7':
            return "Qu???n Tr??? Vi??n"

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
            mo_ta = "Nh??n Vi??n Ph??ng Kh??m"

        return mo_ta

    def is_bac_si_lam_sang(self):
        if self.chuc_nang == '3' or self.is_superuser:
            return True
        else:
            return False

    @staticmethod
    def get_count_in_day(queryset):
        total_count = queryset.aggregate(
            Count('id'))['id__count'] if queryset else 0
        return total_count


class BacSi(models.Model):
    Type = (
        ('full_time', "Full-Time"),
        ('part_time', "Part-Time"),
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True, related_name='user_bac_si')
    chung_chi_hanh_nghe = models.CharField(
        max_length=50, null=True, blank=True)
    gioi_thieu = models.TextField(null=True, blank=True)
    chuc_danh = models.CharField(max_length=255, null=True, blank=True)
    chuyen_khoa = models.CharField(max_length=255, null=True, blank=True)
    noi_cong_tac = models.TextField(null=True, blank=True)
    kinh_nghiem = models.TextField(null=True, blank=True)
    loai_cong_viec = models.CharField(
        null=True, blank=True, choices=Type, max_length=50)

    class Meta:
        verbose_name = "B??c S??"
        verbose_name_plural = "B??c S??"


class TinhTrangPhongKham(models.Model):
    """ M??? r???ng ph???n t??nh tr???ng c???a ph??ng kh??m, khi ph??ng kh??m mu???n t???m ng??ng ho???t ?????ng
    trong m???t kho???ng th???i gian th?? b???ng n??y s??? ???????c s??? d???ng ????? m??? r???ng t??nh n??ng cho b???ng Ph??ng Kh??m """
    kha_dung = models.BooleanField(default=True)
    thoi_gian_dong_cua = models.DateTimeField(null=True, blank=True)
    thoi_gian_mo_cua = models.DateTimeField(null=True, blank=True)

    # t???a ????? ?????a l?? c???a ph??ng kh??m s??? ???????c s??? d???ng ????? hi???n th??? l??n map trong mobile app
    latitude = models.CharField(null=True, blank=True, max_length=50)
    longtitude = models.CharField(null=True, blank=True, max_length=50)

    ip_range_start = models.CharField(max_length=50, null=True, blank=True)
    ip_range_end = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = 'T??nh Tr???ng Ph??ng Kh??m'
        verbose_name_plural = "T??nh Tr???ng Ph??ng Kh??m"


class PhongKham(models.Model):
    """ Th??ng tin chi ti???t c???a ph??ng kh??m """
    file_prepend = "logo_phong_kham/"

    ma_cskcb = models.CharField(max_length=10, null=True, blank=True)

    ten_phong_kham = models.CharField(max_length=255)
    dia_chi = models.TextField(null=True, blank=True)
    so_dien_thoai = models.CharField(max_length=12)
    email = models.EmailField(null=True, blank=True)
    logo = models.FileField(upload_to=file_url, null=True, blank=True)
    tinh_trang = models.ForeignKey(
        TinhTrangPhongKham, on_delete=models.CASCADE)
    gia_tri_diem_tich = models.PositiveIntegerField(null=True, blank=True)
    # NEW
    chu_khoan = models.CharField(max_length=255, null=True, blank=True)
    so_tai_khoan = models.CharField(max_length=20, null=True, blank=True)
    thong_tin_ngan_hang = models.TextField(null=True, blank=True)
    # END

    class Meta:
        verbose_name = "Ph??ng Kh??m"
        verbose_name_plural = "Ph??ng Kh??m"
        permissions = (
            ('can_add_clinic_info', "Th??m th??ng tin ph??ng kh??m"),
            ('can_change_clinic_info', "Thay ?????i th??ng tin ph??ng kh??m"),
        )


class PhongChucNang(models.Model):
    """ M???i d???ch v??? kh??m s??? c?? m???t ph??ng ch???c n??ng ri??ng bi???t, l?? n??i b???nh nh??n sau khi ???????c ph??n d???ch v??? kh??m s??? ?????n trong su???t chu???i kh??m c???a b???nh nh??n """
    ten_phong_chuc_nang = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=True, blank=True)
    bac_si_phu_trach = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="bac_si_chuyen_khoa")
    # dich_vu_kham = models.ForeignKey(DichVuKham, null=True, blank=True, on_delete=models.DO_NOTHING, related_name="phong_chuc_nang_theo_dich_vu")
    thoi_gian_tao = models.DateTimeField(
        editable=False, null=True, blank=True, auto_now_add=True)
    thoi_gian_cap_nhat = models.DateTimeField(
        null=True, blank=True, auto_now=True)

    class Meta:
        verbose_name = "Ph??ng Ch???c N??ng"
        verbose_name_plural = "Ph??ng Ch???c N??ng"
        permissions = (
            ('can_add_consulting_room', 'Th??m ph??ng ch???c n??ng'),
            ('can_change_consulting_room', 'Ch???nh s???a ph??ng ch???c n??ng'),
            ('can_view_consulting_room', 'Xem ph??ng ch???c n??ng'),
            ('can_delete_consulting_room', 'X??a ph??ng ch???c n??ng'),
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
    """ Danh s??ch t???t c??? c??c d???ch v??? kh??m trong ph??ng kh??m """
    khoa = models.ForeignKey(
        "DanhMucKhoa", on_delete=models.SET_NULL, null=True, blank=True)

    ma_dvkt = models.CharField(max_length=50, null=True, blank=True)
    stt = models.CharField(max_length=10, null=True, blank=True, unique=True)
    ten_dvkt = models.CharField(max_length=255, null=True, blank=True)
    ma_gia = models.CharField(max_length=50, null=True, blank=True)
    don_gia = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=0)
    don_gia_bhyt = models.DecimalField(
        null=True, blank=True, max_digits=10, decimal_places=0)
    quyet_dinh = models.CharField(max_length=10, null=True, blank=True)
    cong_bo = models.CharField(max_length=10, null=True, blank=True)
    ma_cosokcb = models.CharField(max_length=20, null=True, blank=True)
    ten_dich_vu = models.CharField(max_length=255, null=True, blank=True)
    bao_hiem = models.BooleanField(default=False)

    nhom_chi_phi = models.ForeignKey(
        'NhomChiPhi', on_delete=models.SET_NULL, null=True, blank=True)
    tyle_tt = models.IntegerField(null=True, blank=True)
    # bac_si_phu_trach = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="bac_si_phu_trach", null=True, blank=True)
    # khoa_kham = models.ForeignKey(KhoaKham, on_delete=models.SET_NULL, related_name="khoa_kham", null=True, blank=True)
    phong_chuc_nang = models.ForeignKey(
        PhongChucNang, on_delete=models.SET_NULL, null=True, blank=True, related_name="dich_vu_kham_theo_phong")

    chi_so = models.BooleanField(default=False)
    html = models.BooleanField(default=False)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    def __str__(self):
        return f'({self.id}){str(self.ten_dvkt)}'

    class Meta:
        verbose_name = "D???ch V??? Kh??m"
        verbose_name_plural = "D???ch V??? Kh??m"
        permissions = (
            ('can_add_service', 'Th??m d???ch v??? k??? thu???t'),
            ('can_add_service_with_excel_file',
             'Th??m d???ch v??? k??? thu???t b???ng Excel File'),
            ('can_change_service', 'Thay ?????i d???ch v??? k??? thu???t'),
            ('can_view_service', 'Xem d???ch v??? k??? thu???t'),
            ('can_delete_service', 'X??a d???ch v??? k??? thu???t'),
            ('can_view_service_price', 'Xem gi?? d???ch v??? k??? thu???t'),
            ('can_export_list_of_service', 'Xu???t danh s??ch d???ch v??? k??? thu???t'),
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
    """ B???ng gi?? s??? l??u tr??? t???t c??? gi?? c???a d???ch v??? kh??m v?? c??? thu???c """
    id_dich_vu_kham = models.OneToOneField(
        DichVuKham, null=True, blank=True, on_delete=models.PROTECT, related_name="gia_dich_vu_kham")
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
    """ B???ng B???o Hi???m s??? l??u tr??? t???t c??? c??c lo???i b???o hi???m ??p d???ng trong ph??ng kh??m """
    ten_bao_hiem = models.CharField(max_length=255)
    # d???ng b???o hi???m ??? ????y l?? s??? % ???????c b???o hi???m chi tr???
    dang_bao_hiem = models.SmallIntegerField(null=True, blank=True)
    id_dich_vu_kham = models.OneToOneField(
        DichVuKham, null=True, blank=True, on_delete=models.PROTECT, related_name="bao_hiem_dich_vu_kham")
    # id_thuoc = models.ForeignKey(Thuoc, on_delete=models.PROTECT, null=True, blank=True, related_name="bao_hiem_thuoc")
    thoi_gian_tao = models.DateTimeField()
    thoi_gian_chinh_sua = models.DateTimeField()

    def save(self, *agrs, **kwargs):
        if not self.id:
            self.thoi_gian_tao = timezone.now()
        self.thoi_gian_chinh_sua = timezone.now()
        return super(BaoHiem, self).save(*agrs, **kwargs)


class ProfilePhongChucNang(models.Model):
    phong_chuc_nang = models.OneToOneField(
        PhongChucNang, on_delete=models.CASCADE, related_name="profile_phong_chuc_nang")
    so_luong_cho = models.PositiveIntegerField(null=True, blank=True)
    thoi_gian_trung_binh = models.PositiveIntegerField(
        help_text="????n v???(ph??t)", null=True, blank=True)
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
        verbose_name = "Tr???ng Th??i L???ch H???n"
        verbose_name_plural = "Tr???ng Th??i L???ch H???n"

    def __str__(self):
        return f"({self.id})" + self.ten_trang_thai


def get_default_trang_thai_lich_hen():
    return TrangThaiLichHen.objects.get_or_create(ten_trang_thai="???? ?????t tr?????c")[0]


today = timezone.localtime(timezone.now())
tomorrow = today + timedelta(1)
today_start = today.replace(hour=0, minute=0, second=0)
today_end = tomorrow.replace(hour=0, minute=0, second=0)

# class LichHenKhamManager(models.Manager):
#     def lich_hen_hom_nay(self):
#         return self.filter(thoi_gian_bat_dau__lte = today_end, thoi_gian_ket_thuc__gte = today_start)


class LichHenKham(models.Model):

    LYDO_VVIEN = (
        ("1", "????ng Tuy???n"),
        ("2", "C???p C???u"),
        ("3", "Tr??i Tuy???n"),
        ("4", "Th??ng Tuy???n"),
    )

    LOAI_DICH_VU = (
        ('kham_chua_benh', 'Kh??m Ch???a B???nh'),
        ('kham_suc_khoe', 'Kh??m S???c Kh???e'),
        ('kham_theo_yeu_cau', 'Kh??m Theo Y??u C???u'),
    )

    ma_lich_hen = models.CharField(max_length=15, null=True, blank=True)
    benh_nhan = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="benh_nhan_hen_kham")
    nguoi_phu_trach = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="nguoi_phu_trach")

    thoi_gian_bat_dau = models.DateTimeField()
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)
    ly_do = models.TextField(null=True, blank=True)
    dia_diem = models.CharField(max_length=255, null=True, blank=True)
    loai_dich_vu = models.CharField(
        choices=LOAI_DICH_VU, null=True, blank=True, max_length=25)
    trang_thai = models.ForeignKey(
        TrangThaiLichHen, on_delete=models.CASCADE, null=True, blank=True)

    ly_do_vvien = models.CharField(
        max_length=5, choices=LYDO_VVIEN, null=True, blank=True)
    thanh_toan_sau = models.BooleanField(default=False)

    thoi_gian_tao = models.DateTimeField(
        editable=False, null=True, blank=True, auto_now_add=True)
    thoi_gian_chinh_sua = models.DateTimeField(
        null=True, blank=True, auto_now=True)

    class Meta:
        verbose_name = "L???ch H???n Kh??m"
        verbose_name_plural = "L???ch H???n Kh??m"
        permissions = (
            ('can_add_appointment', 'Th??m l???ch h???n'),
            ('can_change_appointment', 'Thay ?????i l???ch h???n'),
            ('can_view_appointment', 'Xem l???ch h???n'),
            ('can_delete_appointment', 'X??a l???ch h???n'),
            ('can_make_reexamination', 'Th??m l???ch h???n t??i kh??m'),
            ('can_confirm_appoinment', 'X??c nh???n l???ch h???n'),
            ('can_confirm_do_examination', 'X??c nh???n kh??m'),
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
                trang_thai_chuoi_kham = TrangThaiChuoiKham.objects.get(
                    trang_thai_chuoi_kham='Ho??n Th??nh')
                if chuoi_kham.trang_thai == trang_thai_chuoi_kham:
                    hoan_thanh_kham = True

        return hoan_thanh_kham

    @staticmethod
    def get_count_in_day(queryset):
        total_count = queryset.values(
            'benh_nhan__id').distinct().count() if queryset else 0
        return total_count

    def get_id_chuoi_kham(self):
        if self.danh_sach_chuoi_kham.exists():
            chuoi_kham = self.danh_sach_chuoi_kham.all().last()
            id_chuoi_kham = chuoi_kham.id
            return id_chuoi_kham
        else:
            return ""


class LichSuTrangThaiLichHen(models.Model):
    lich_hen_kham = models.ForeignKey(
        LichHenKham, on_delete=models.CASCADE, related_name="lich_hen")
    trang_thai_lich_hen = models.ForeignKey(
        TrangThaiLichHen, on_delete=models.CASCADE, related_name="trang_thai_lich_hen")
    # N??u r?? nguy??n nh??n d???n ?????n tr???ng th??i ????
    chi_tiet_trang_thai = models.CharField(
        max_length=500, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True)


def get_sentinel_dich_vu():
    return DichVuKham.objects.get_or_create(ten_dich_vu='deleted')[0]


class TrangThaiKhoaKham(models.Model):
    """ T???t c??? c??c tr???ng th??i c?? th??? x???y ra trong ph??ng kh??m """
    trang_thai_khoa_kham = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Tr???ng Th??i Khoa Kh??m"
        verbose_name_plural = "Tr???ng Th??i Khoa Kh??m"

    def __str__(self):
        return f"({self.id})" + self.trang_thai_khoa_kham


class TrangThaiChuoiKham(models.Model):
    trang_thai_chuoi_kham = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Tr???ng Th??i Chu???i Kh??m"
        verbose_name_plural = "Tr???ng Th??i Chu???i Kh??m"

    def __str__(self):
        return f"({self.id})" + self.trang_thai_chuoi_kham


def get_default_trang_thai_chuoi_kham():
    return TrangThaiChuoiKham.objects.get_or_create(trang_thai_chuoi_kham="??ang ch???")[0]


def get_default_trang_thai_khoa_kham():
    return TrangThaiKhoaKham.objects.get_or_create(trang_thai_khoa_kham="??ang ch???")[0]


class ChuoiKham(models.Model):
    """ M???i b???nh nh??n khi t???i ph??ng kh??m ????? sau khi kh??m t???ng qu??t th?? ?????u s??? c?? m???t chu???i kh??m.
    Do chu???i kh??m n??y c?? t??nh t??ch l??y n??n b???nh nh??n c?? th??? d??? d??ng xem l???i ???????c l???ch s??? kh??m c???a m??nh k???t h???p v???i c??c k???t qu??? kh??m t???i ph??ng kh??m """
    ma_lk = models.CharField(max_length=100, null=True, blank=True)
    benh_nhan = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chuoi_kham")
    bac_si_dam_nhan = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="bac_si_chuoi_kham", null=True, blank=True)
    lich_hen = models.ForeignKey(LichHenKham, on_delete=models.CASCADE,
                                 null=True, blank=True, related_name='danh_sach_chuoi_kham')
    thoi_gian_bat_dau = models.DateTimeField(null=True, blank=True)
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)
    thoi_gian_tai_kham = models.DateTimeField(null=True, blank=True)
    trang_thai = models.ForeignKey(
        TrangThaiChuoiKham, on_delete=models.CASCADE, related_name="trang_thai", null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(
        auto_now_add=True, blank=True, null=True)
    thoi_gian_cap_nhat = models.DateTimeField(
        auto_now=True, blank=True, null=True)

    class Meta:
        verbose_name = "Chu???i Kh??m"
        verbose_name_plural = "Chu???i Kh??m"
        permissions = (
            ('can_add_assignment_chain', 'Th??m chu???i kh??m'),
            ('can_change_assignment_chain', 'Thay ?????i chu???i kh??m'),
            ('can_view_assignment_chain', 'Xem chu???i kh??m'),
            ('can_view_assignment_chain_result', 'Xem k???t qu??? chu???i kh??m'),
            ('can_delete_assignment_chain', 'X??a chu???i kh??m'),
            ('can_delete_assignment_chain_result', 'X??a k???t qu??? chu???i kh??m'),
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
        da_thanh_toan = TrangThaiChuoiKham.objects.filter(
            trang_thai_chuoi_kham='???? Thanh To??n').first()
        if self.trang_thai == da_thanh_toan:
            return True
        else:
            return False

    def check_thanh_toan(self):
        flag = False
        try:
            hoa_don_dich_vu = self.hoa_don_dich_vu
            if hoa_don_dich_vu.tong_tien is not None:
                flag = True
        except HoaDonChuoiKham.DoesNotExist:
            flag = False
        return flag
      
    def check_thanh_toan_them(self):
        flag = False
        if self.check_thanh_toan():
            tong_tien_thanh_toan = self.hoa_don_dich_vu.tong_tien
            tong_tien_phan_khoa = self.phan_khoa_kham.all().aggregate(
                tong_tien=Sum('dich_vu_kham__don_gia'))['tong_tien']
            if int(tong_tien_phan_khoa) > int(tong_tien_thanh_toan):
                flag = True
        return flag

    def get_tong_tien_phan_khoa(self):
        total = 0
        for phan_khoa in self.phan_khoa_kham.all():
            total += phan_khoa.get_gia_dich_vu()
        return total


class InPaidBilledManager(models.Manager):
    def get_queryset(self):
        return super(InPaidBilledManager, self).get_queryset().filter(check_exists_in_paid_bill=True)


class PhanKhoaKham(models.Model):
    benh_nhan = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True)
    dich_vu_kham = models.ForeignKey(
        DichVuKham, on_delete=models.SET_NULL, null=True, blank=True, related_name="phan_khoa_dich_vu")
    bac_si_lam_sang = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="bac_si", null=True)
    chuoi_kham = models.ForeignKey(
        ChuoiKham, on_delete=models.CASCADE, null=True, blank=True, related_name="phan_khoa_kham")
    bao_hiem = models.BooleanField(default=False)

    priority = models.SmallIntegerField(null=True, blank=True)

    thoi_gian_bat_dau = models.DateTimeField(null=True, blank=True)
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)

    trang_thai = models.ForeignKey(
        TrangThaiKhoaKham, on_delete=models.SET_NULL, null=True)

    thoi_gian_tao = models.DateTimeField(
        null=True, blank=True, auto_now_add=True)
    thoi_gian_cap_nhat = models.DateTimeField(
        null=True, blank=True, auto_now=True)

    objects = models.Manager()
    in_paid_bill = InPaidBilledManager()

    class Meta:
        verbose_name = "Ph??n Khoa Kh??m"
        verbose_name_plural = "Ph??n Khoa Kh??m"
        permissions = (
            ('can_add_service_assignment', 'Th??m ph??n khoa kh??m'),
            ('can_view_service_assignment', 'Xem ph??n khoa kh??m'),
            ('can_delete_service_assignment', 'X??a ph??n khoa kh??m'),
            ('can_do_specialist_examination', 'C?? th??? kh??m chuy??n khoa'),
            ('can_stop_serivce_assignment', 'D???ng kh??m'),
        )

    def get_ten_benh_nhan(self):
        if self.benh_nhan is not None:
            return self.benh_nhan.ho_ten
        else:
            return "Kh??ng x??c ?????nh"

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
            return "Kh??ng c?? ?????a ch???"

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
                return "N???"
            else:
                return "Kh??ng x??c ?????nh"
        else:
            return "Kh??ng x??c ?????nh"

    def get_bac_si_chi_dinh(self):
        if self.bac_si_lam_sang is not None:
            return self.bac_si_lam_sang.ho_ten
        else:
            return "Kh??ng c??"

    def gia_dich_vu_theo_bao_hiem(self):
        gia = self.dich_vu_kham.gia_dich_vu_kham.gia
        if self.bao_hiem:
            tong_tien = gia * \
                decimal.Decimal(
                    (1 - (self.dich_vu_kham.bao_hiem_dich_vu_kham.dang_bao_hiem / 100)))
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

    def get_gia_dich_vu(self):
        if self.dich_vu_kham is not None:
            tong_tien = int(self.dich_vu_kham.don_gia)
        else:
            tong_tien = 0

        return tong_tien

    def check_exists_in_paid_bill(self):
        flag = False
        if self.chuoi_kham is not None:
            if self.chuoi_kham.hoa_don_dich_vu is not None:
                if self.chuoi_kham.hoa_don_dich_vu.tong_tien is not None:
                    flag = True
        return flag

    @property
    def check_chuoi_kham_has_timestart(self):
        flag = False
        if self.chuoi_kham is not None:
            if self.chuoi_kham.thoi_gian_bat_dau is not None:
                flag = True

        return flag

    @property
    def check_chuoi_kham_has_timeend(self):
        flag = False
        if self.chuoi_kham is not None:
            if self.chuoi_kham.thoi_gian_ket_thuc is not None:
                flag = True
        return flag


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
    phan_khoa_kham = models.ForeignKey(
        PhanKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    trang_thai_khoa_kham = models.ForeignKey(
        TrangThaiKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    # N??u r?? nguy??n nh??n d???n t???i tr???ng th??i ????
    chi_tiet_trang_thai = models.CharField(
        max_length=500, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True)


class LichSuChuoiKham(models.Model):
    chuoi_kham = models.ForeignKey(
        ChuoiKham, on_delete=models.CASCADE, null=True, blank=True)
    trang_thai = models.ForeignKey(
        TrangThaiChuoiKham, on_delete=models.CASCADE, null=True, blank=True)
    # N??u r?? nguy??n nh??n d???n t???i tr???ng th??i ????
    chi_tiet_trang_thai = models.CharField(
        max_length=500, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True)


class KetQuaTongQuat(models.Model):
    """ K???t qu??? t???ng qu??t c???a ng?????i d??ng sau m???t l???n ?????n th??m kh??m t???i ph??ng kh??m """

    RESULT_CHOICES = (
        ("1", "Kh???i"),
        ("2", "?????"),
        ("3", "Kh??ng Thay ?????i"),
        ("4", "N???ng H??n"),
        ("5", "T??? Vong"),
    )

    chuoi_kham = models.ForeignKey(
        ChuoiKham, on_delete=models.SET_NULL, null=True, related_name="ket_qua_tong_quat")
    # benh_nhan = models.ForeignKey(User, on_delete=models.SET(get_sentinel_user))
    ma_benh = models.ForeignKey(
        'DanhMucBenh', on_delete=models.SET_NULL, null=True, blank=True)
    ma_ket_qua = models.CharField(max_length=50, null=True, blank=True)
    mo_ta = models.CharField(max_length=255, null=True, blank=True)
    ket_luan = models.TextField(null=True, blank=True)

    ket_qua_dieu_tri = models.CharField(
        max_length=5, choices=RESULT_CHOICES, null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "K???t Qu??? T???ng Qu??t"
        verbose_name_plural = "K???t Qu??? T???ng Qu??t"
        permissions = (
            ('can_add_general_result', 'Th??m k???t qu??? t???ng qu??t'),
            ('can_view_general_result', 'Xem k???t qu??? t???ng qu??t'),
            ('can_change_general_result', 'Thay ?????i k???t qu??? t???ng qu??t'),
            ('can_delete_general_result', 'X??a k???t qu??? t???ng qu??t'),
        )

    def get_mo_ta(self):
        if not self.mo_ta:
            return "Kh??ng c?? m?? t???"
        return self.mo_ta

    def get_ket_luan(self):
        if not self.ket_luan:
            return "Kh??ng c?? k???t lu???n"
        return self.ket_luan

    @property
    def check_html_ket_qua(self):
        if self.html_ket_qua_tong_quat.exists():
            return True
        else:
            return False


class KetQuaChuyenKhoa(models.Model):
    """ K???t qu??? c???a kh??m chuy??n khoa m?? ng?????i d??ng c?? th??? nh???n ???????c """
    ma_ket_qua = models.CharField(
        max_length=50, null=True, blank=True, unique=True)
    bac_si_chuyen_khoa = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ket_qua_bac_si_chuyen_khoa')
    phan_khoa_kham = models.ForeignKey(
        PhanKhoaKham, on_delete=models.CASCADE, null=True, blank=True, related_name="ket_qua_chuyen_khoa")
    ket_qua_tong_quat = models.ForeignKey(
        KetQuaTongQuat, on_delete=models.CASCADE, related_name="ket_qua_chuyen_khoa")
    mo_ta = models.CharField(max_length=255, null=True, blank=True)
    ket_luan = models.TextField(null=True, blank=True)

    chi_so = models.BooleanField(default=False)
    html = models.BooleanField(default=False)

    thoi_gian_tao = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "K???t Qu??? Chuy??n Khoa"
        verbose_name_plural = "K???t Qu??? Chuy??n Khoa"
        permissions = (
            ('can_add_specialty_result', 'Th??m k???t qu??? chuy??n khoa'),
            ('can_view_specialty_result', 'Xem k???t qu??? chuy??n khoa'),
            ('can_change_specialty_result', 'Thay ?????i k???t qu??? chuy??n khoa'),
            ('can_delete_specialty_result', 'X??a k???t qu??? chuy??n khoa'),
            ('can_view_history_specialty_result', 'Xem l???ch s??? kh??m chuy??n khoa'),
        )

    def get_mo_ta(self):
        if not self.mo_ta:
            return "Kh??ng c?? m?? t???"
        return self.mo_ta

    def get_ket_luan(self):
        if not self.ket_luan:
            return "Kh??ng c?? k???t lu???n"
        return self.ket_luan

    def get_ten_dich_vu(self):
        if self.phan_khoa_kham is not None:
            if self.phan_khoa_kham.dich_vu_kham is not None:
                return self.phan_khoa_kham.dich_vu_kham.ten_dvkt
            else:
                return "Kh??ng x??c ?????nh"
        else:
            return "Kh??ng x??c ?????nh"


key_store = FileSystemStorage()


class FileKetQua(models.Model):
    """ File k???t qu??? c???a m???i ng?????i d??ng """
    file_prepend = 'user/documents/'
    file = models.FileField(upload_to=file_url, null=True,
                            blank=True, storage=key_store)
    # file = models.CharField(max_length=500, null=True, blank=True)
    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "T??i Li???u"
        verbose_name_plural = "T??i Li???u"

    def __unicode__(self):
        return self.file.url

    def filename(self):
        return os.path.basename(self.file.name)

    def get_url(self):
        return self.file.url
    # ket_qua_chuyen_khoa = models.ForeignKey(KetQuaChuyenKhoa, on_delete=models.SET_NULL, null=True, blank=True, related_name="file_ket_qua_chuyen_khoa")
    # ket_qua_tong_quat = models.ForeignKey(KetQuaTongQuat, on_delete=models.SET_NULL, null=True, blank=True, related_name="file_ket_qua_tong_quat")


class FileKetQuaTongQuat(models.Model):
    file = models.ForeignKey(
        FileKetQua, on_delete=models.CASCADE, related_name="file_tong_quat")
    ket_qua_tong_quat = models.ForeignKey(
        KetQuaTongQuat, on_delete=models.CASCADE, related_name="file_ket_qua_tong_quat")

    class Meta:
        verbose_name = "File K???t Qu??? T???ng Qu??t"
        verbose_name_plural = "File K???t Qu??? T???ng Qu??t"


class FilePhongKham(models.Model):
    file_prepend = 'phongkham/documents/'
    file = models.FileField(upload_to=file_url, null=True,
                            blank=True, storage=key_store)

    thoi_gian_tao = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "T??i Li???u Ph??ng Kh??m"
        verbose_name_plural = "T??i Li???u Ph??ng Kh??m"


class FileKetQuaChuyenKhoa(models.Model):
    file = models.ForeignKey(
        FileKetQua, on_delete=models.CASCADE, related_name="file_chuyen_khoa")
    ket_qua_chuyen_khoa = models.ForeignKey(
        KetQuaChuyenKhoa, on_delete=models.CASCADE, related_name="file_ket_qua_chuyen_khoa")

    class Meta:
        verbose_name = "File K???t Qu??? Chuy??n Khoa"
        verbose_name_plural = "File K???t Qu??? Chuy??n Khoa"


CharField.register_lookup(Lower)


class BaiDang(models.Model):
    file_prepend = 'bai_dang/'
    tieu_de = models.CharField(null=True, blank=True, max_length=1024)
    hinh_anh = models.ImageField(upload_to=file_url, null=True, blank=True)
    noi_dung_chinh = models.TextField(null=True, blank=True)
    noi_dung = models.TextField(null=True, blank=True)
    thoi_gian_bat_dau = models.DateTimeField(null=True, blank=True)
    thoi_gian_ket_thuc = models.DateTimeField(null=True, blank=True)
    nguoi_dang_bai = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name="nguoi_dang_bai", null=True, blank=True)

    thoi_gian_tao = models.DateTimeField(
        auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name = "B??i ????ng"
        verbose_name_plural = "B??i ????ng"
        permissions = (
            ('can_add_news', 'Th??m b??i ????ng'),
            ('can_change_news', 'Thay ?????i b??i ????ng'),
            ('can_view_news', 'Xem b??i ????ng'),
            ('can_delete_news', 'X??a b??i ????ng'),
        )

    def get_truncated_noi_dung_chinh(self):
        noi_dung_chinh = (self.noi_dung_chinh[:75] + '...') if len(
            self.noi_dung_chinh) > 75 else self.noi_dung_chinh
        return noi_dung_chinh

# * ------ Update 19/01 -------


class NhomChiSoXetNghiem(models.Model):
    ten_nhom = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Nh??m Ch??? S??? X??t Nghi???m"
        verbose_name_plural = "Nh??m Ch??? S??? X??t Nghi???m"

    def __str__(self):
        return f"({self.id}){self.ten_nhom}"


class ChiSoXetNghiem(models.Model):
    dich_vu_kham = models.ForeignKey(
        DichVuKham, on_delete=models.CASCADE, null=True, blank=True, related_name="chi_so_xet_nghiem")
    doi_tuong_xet_nghiem = models.ForeignKey(
        "DoiTuongXetNghiem", on_delete=models.SET_NULL, null=True, blank=True)
    nhom_chi_so = models.ForeignKey(
        "NhomChiSoXetNghiem", on_delete=models.CASCADE, null=True, blank=True)
    ma_chi_so = models.CharField(max_length=10, null=True, blank=True)
    ten_chi_so = models.CharField(max_length=255, null=True, blank=True)
    chi_tiet = models.ForeignKey(
        "ChiTietChiSoXetNghiem", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Ch??? S??? X??t Nghi???m"
        verbose_name_plural = "Ch??? S??? X??t Nghi???m"
        permissions = (
            ('can_add_test_values', 'Th??m ch??? s??? x??t nghi???m'),
            ('can_change_test_values', 'Thay ?????i ch??? s??? x??t nghi???m'),
            ('can_view_test_values', 'Xem ch??? s??? x??t nghi???m'),
            ('can_delete_test_values', 'X??a ch??? s??? x??t nghi???m'),
        )

    def __str__(self):
        return f"({self.ma_chi_so}){self.ten_chi_so}/{self.doi_tuong_xet_nghiem}"


class ChiTietChiSoXetNghiem(models.Model):
    chi_so_binh_thuong_min = models.CharField(
        null=True, blank=True, max_length=10)
    chi_so_binh_thuong_max = models.CharField(
        null=True, blank=True, max_length=10)
    chi_so_binh_thuong = models.CharField(null=True, blank=True, max_length=10)
    don_vi_do = models.CharField(max_length=50, null=True, blank=True)
    ghi_chu = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        verbose_name = "Chi Ti???t Ch??? S??? X??t Nghi???m"
        verbose_name_plural = "Chi Ti???t Ch??? S??? X??t Nghi???m"

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
        (FEMALE, "N???"),
        (UNDEFINED, "Ch??a X??c ?????nh"),
    )
    gioi_tinh = models.CharField(
        choices=gender_choices, max_length=5, null=True, blank=True)
    do_tuoi = models.ForeignKey(
        'DoTuoiXetNghiem', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "?????i T?????ng X??t Nghi???m"
        verbose_name_plural = "?????i T?????ng X??t Nghi???m"

    def __str__(self):
        if self.gioi_tinh == "1":
            return f"Nam({self.do_tuoi})"
        elif self.gioi_tinh == "2":
            return f"N???({self.do_tuoi})"
        else:
            return f"Kh??ng X??c ?????nh({self.do_tuoi})"


class DoTuoiXetNghiem(models.Model):
    do_tuoi_min = models.PositiveIntegerField(null=True, blank=True)
    do_tuoi_max = models.PositiveIntegerField(null=True, blank=True)
    ghi_chu = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "????? Tu???i X??t Nghi???m"
        verbose_name_plural = "????? Tu???i X??t Nghi???m"

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
        (OK, "B??nh th?????ng"),
        (NG, "B???t b??nh th?????ng"),
    )
    phan_khoa_kham = models.ForeignKey(
        PhanKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    ket_qua_chuyen_khoa = models.ForeignKey(
        KetQuaChuyenKhoa, on_delete=models.CASCADE, null=True, blank=True, related_name="ket_qua_xet_nghiem")
    chi_so_xet_nghiem = models.ForeignKey(
        ChiSoXetNghiem, on_delete=models.SET_NULL, null=True, blank=True)
    ket_qua_xet_nghiem = models.CharField(max_length=50, null=True, blank=True)
    danh_gia_chi_so = models.CharField(
        choices=judment_choices, max_length=5, null=True, blank=True)
    danh_gia_ghi_chu = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "K???t Qu??? X??t Nghi???m"
        verbose_name_plural = "K???t Qu??? X??t Nghi???m"
        permissions = (
            ('can_add_lab_result', 'Th??m k???t qu??? x??t nghi???m'),
            ('can_change_lab_result', 'Thay ?????i k???t qu??? x??t nghi???m'),
            ('can_view_lab_result', 'Xem k???t qu??? x??t nghi???m'),
            ('can_delete_lab_result', 'X??a k???t qu??? x??t nghi???m'),
        )

    def get_ten_chi_so(self):
        if self.chi_so_xet_nghiem is not None:
            return self.chi_so_xet_nghiem.ten_chi_so
        else:
            return "Kh??ng x??c ?????nh"

    def get_chi_so_min(self):
        if self.chi_so_xet_nghiem is not None:
            if self.chi_so_xet_nghiem.chi_tiet is not None:
                return self.chi_so_xet_nghiem.chi_tiet.chi_so_binh_thuong_min
            else:
                return 0
        else:
            return "Kh??ng x??c ?????nh"

    def get_chi_so_max(self):
        if self.chi_so_xet_nghiem is not None:
            if self.chi_so_xet_nghiem.chi_tiet is not None:
                return self.chi_so_xet_nghiem.chi_tiet.chi_so_binh_thuong_max
            else:
                return 0
        else:
            return "Kh??ng x??c ?????nh"

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
            return "Kh??ng c??"
        else:
            return self.ket_qua_xet_nghiem

    def get_ten_dvkt(self):
        return self.phan_khoa_kham.dich_vu_kham.ten_dvkt


class HtmlKetQua(models.Model):
    phan_khoa_kham = models.ForeignKey(
        PhanKhoaKham, on_delete=models.CASCADE, null=True, blank=True)
    ket_qua_tong_quat = models.ForeignKey(
        KetQuaTongQuat, on_delete=models.CASCADE, null=True, blank=True, related_name="html_ket_qua_tong_quat")
    ket_qua_chuyen_khoa = models.ForeignKey(
        KetQuaChuyenKhoa, on_delete=models.CASCADE, null=True, blank=True, related_name="html_ket_qua")
    noi_dung = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = "K???t Qu??? D???ng HTML"
        verbose_name_plural = "K???t Qu??? D???ng HTML"


class DanhMucChuongBenh(models.Model):
    stt = models.CharField(max_length=5, null=True, blank=True)
    ma_chuong = models.CharField(max_length=15, null=True, blank=True)
    ten_chuong = models.CharField(max_length=255, null=True, blank=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Danh M???c Ch????ng B???nh"
        verbose_name_plural = "Danh M???c Ch????ng B???nh"

    def __str__(self):
        return self.stt + f" ({self.ma_chuong})"


class DanhMucNhomBenh(models.Model):
    chuong_benh = models.ForeignKey(
        DanhMucChuongBenh, on_delete=models.CASCADE, null=True, blank=True, related_name="nhom_benh")
    ma_nhom_chinh = models.CharField(max_length=15, null=True, blank=True)
    ten_nhom_chinh = models.CharField(max_length=255, null=True, blank=True)
    ma_nhom_phu_1 = models.CharField(max_length=15, null=True, blank=True)
    ten_nhom_phu_1 = models.CharField(max_length=255, null=True, blank=True)
    ma_nhom_phu_2 = models.CharField(max_length=15, null=True, blank=True)
    ten_nhom_phu_2 = models.CharField(max_length=255, null=True, blank=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Danh M???c Nh??m B???nh"
        verbose_name_plural = "Danh M???c Nh??m B???nh"

    def __str__(self):
        return self.ten_nhom_chinh


class DanhMucLoaiBenh(models.Model):
    nhom_benh = models.ForeignKey(
        DanhMucNhomBenh, on_delete=models.CASCADE, null=True, blank=True, related_name="loai_benh")
    ma_loai = models.CharField(max_length=10, null=True, blank=True)
    ten_loai = models.CharField(max_length=255, null=True, blank=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Danh M???c Lo???i B???nh"
        verbose_name_plural = "Danh M???c Lo???i B???nh"

    def __str__(self):
        return self.ten_loai


class DanhMucBenh(models.Model):
    loai_benh = models.ForeignKey(
        DanhMucLoaiBenh, on_delete=models.CASCADE, null=True, blank=True, related_name="benh")
    ma_benh = models.CharField(max_length=15, null=True, blank=True)
    ten_benh = models.CharField(max_length=1024, null=True, blank=True)
    ma_nhom_bcao_byt = models.CharField(max_length=5, null=True, blank=True)
    ma_nhom_chi_tiet = models.CharField(max_length=10, null=True, blank=True)

    objects = BulkUpdateOrCreateQuerySet.as_manager()

    class Meta:
        verbose_name = "Danh M???c B???nh"
        verbose_name_plural = "Danh M???c B???nh"

    def __str__(self):
        return self.ten_benh


class NhomChiPhi(models.Model):
    ma_nhom = models.CharField(max_length=2, null=True, blank=True)
    ten_nhom = models.CharField(max_length=255, null=True, blank=True)
    ghi_chu = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Nh??m Chi Ph??"
        verbose_name_plural = "Nh??m Chi Ph??"

    def __str__(self):
        return f"({self.ma_nhom}) {self.ten_nhom}"


class NhomTaiNan(models.Model):
    ma_nhom = models.CharField(max_length=2, null=True, blank=True)
    ten_nhom = models.CharField(max_length=100, null=True, blank=True)
    ghi_chu = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Nh??m Tai N???n"
        verbose_name_plural = "Nh??m Tai N???n"

    def __str__(self):
        return self.ten_nhom


class DanhMucKhoa(models.Model):
    stt = models.IntegerField(null=True, blank=True)
    ma_khoa = models.CharField(max_length=5, null=True, blank=True)
    ten_khoa = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Danh M???c Khoa"
        verbose_name_plural = "Danh M???c Khoa"

    def __str__(self):
        return self.ten_khoa


class ThietBi(models.Model):
    ma_may = models.CharField(max_length=50, null=True, blank=True)
    ten_may = models.CharField(max_length=255, null=True, blank=True)
    ghi_chu = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "Thi???t B???"
        verbose_name_plural = "Thi???t B???"

    def __str__(self):
        return self.ten_may


class GoiThau(models.Model):
    ma_goi = models.CharField(max_length=5, null=True, blank=True)
    goi = models.CharField(max_length=255, null=True, blank=True)
    nhom = models.CharField(max_length=255, null=True, blank=True)
    ma_nhom = models.CharField(max_length=5, null=True, blank=True)

    class Meta:
        verbose_name = "G??i Th???u"
        verbose_name_plural = "G??i Th???u"


class DuongDungThuoc(models.Model):
    stt = models.IntegerField(null=True, blank=True)
    ma_duong_dung = models.CharField(max_length=5, null=True, blank=True)
    ten_duong_dung = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "???????ng D??ng Thu???c"
        verbose_name_plural = "???????ng D??ng Thu???c"


class MauPhieu(models.Model):
    dich_vu = models.ForeignKey(
        DichVuKham, on_delete=models.SET_NULL, null=True, blank=True, related_name="mau_phieu")
    ten_mau = models.CharField(max_length=255, null=True, blank=True)
    codename = models.CharField(
        max_length=255, null=True, blank=True, unique=True)
    noi_dung = models.TextField()

    thoi_gian_tao = models.DateTimeField(editable=False, null=True, blank=True)
    thoi_gian_cap_nhat = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.ten_mau

    class Meta:
        verbose_name = "M???u Phi???u"
        verbose_name_plural = "M???u Phi???u"
        permissions = (
            ('can_add_analysis_note', 'Th??m m???u phi???u'),
            ('can_change_analysis_note', 'Thay ?????i m???u phi???u'),
            ('can_view_analysis_note', 'Xem m???u phi???u'),
            ('can_delete_analysis_note', 'X??a m???u phi???u'),
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
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, related_name="district")
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name


class Ward(models.Model):
    id = models.IntegerField(primary_key=True, unique=True)
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="ward")
    name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.name
