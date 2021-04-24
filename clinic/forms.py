from .models import ( 
    BaiDang, FileKetQua, 
    FileKetQuaTongQuat, 
    GiaDichVu, 
    KetQuaTongQuat, MauPhieu, 
    PhongChucNang, PhongKham, 
    User,
    DichVuKham,
    LichHenKham,
    BacSi
)

from django.forms import fields
from medicine.models import CongTy, Thuoc, VatTu
from django import forms
from django.forms.widgets import PasswordInput
# from clinic.models import FileKetQua, FileKetQuaChuyenKhoa, FileKetQuaTongQuat, KetQuaChuyenKhoa, KetQuaTongQuat, User, LichHenKham, DichVuKham, GiaDichVu, BaoHiem, PhongChucNang

class UserRegisterFrom(forms.ModelForm):
    ho_ten = forms.CharField(max_length=255)
    so_dien_thoai = forms.CharField(max_length=12)
    password = forms.CharField(widget=PasswordInput)

    class Meta:
        model = User
        fields = ["ho_ten", "so_dien_thoai", "password"]

class LichHenKhamForm(forms.ModelForm):
    benh_nhan = User.objects.filter(chuc_nang='1')
    class Meta:
        model = LichHenKham
        fields = ['benh_nhan', 'thoi_gian_bat_dau', 'thoi_gian_ket_thuc']

class DichVuKhamForm(forms.ModelForm):
    phong_chuc_nang = forms.ModelChoiceField(queryset=PhongChucNang.objects.all())
    class Meta:
        model = DichVuKham
        fields = '__all__'

class GiaDichVuForm(forms.ModelForm):
    class Meta:
        model = GiaDichVu
        fields = ['gia',]


class PhongChucNangForm(forms.ModelForm):
    class Meta:
        model = PhongChucNang
        fields = ['ten_phong_chuc_nang']

class KetQuaTongQuatForm(forms.ModelForm):
    # benh_nhan = User.objects.filter(chuc_nang='1')
    file = forms.ModelChoiceField(queryset=FileKetQua.objects.all(), required=False)

    class Meta:
        model = KetQuaTongQuat
        fields = ('ma_ket_qua', 'mo_ta', 'ket_luan')

    def init(self, *args, **kwargs):
        super(KetQuaTongQuatForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['file'].initial = FileKetQua.objects.get(file_tong_quat__ket_qua_tong_quat = self.instance).values_list('id', flat=True)
    
    def save(self, commit=True):
        super(KetQuaTongQuatForm, self).save(commit)
        file = self.cleaned_data.pop('file', None)
        if file:
            self.instance.file_ket_qua_tong_quat.delete()
            FileKetQuaTongQuat.objects.create(ket_qua_tong_quat = self.instance, file=file)

class CongTyForm(forms.ModelForm):
    class Meta:
        model = CongTy
        fields = '__all__'

class ThuocForm(forms.ModelForm):
    mo_ta = forms.CharField(widget=forms.Textarea)
    tac_dung_phu = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Thuoc
        fields = '__all__'

class UserForm(forms.ModelForm):
    ngay_sinh = forms.DateTimeField(input_formats=["%d/%m/%Y"])
    class Meta:
        model = User
        fields = '__all__'

# UPDATE BY LONG
class BacSiForm(forms.ModelForm):
    class Meta: 
        model = BacSi
        fields = '__all__'

# END

# NEW BY LONG 8/1
class PhongKhamForm(forms.ModelForm):
    class Meta:
        model = PhongKham
        fields = '__all__'
# END NEW

# NEW 13/1
class VatTuForm(forms.ModelForm):
    class Meta:
        model = VatTu
        fields = '__all__'
# END NEW 13/1

class MauPhieuForm(forms.ModelForm):
    class Meta:
        model = MauPhieu
        fields = ('dich_vu', 'ten_mau', 'noi_dung')

class MauHoaDonForm(forms.ModelForm):
    class Meta:
        model = MauPhieu
        fields = ('ten_mau', 'codename', 'noi_dung')

class BaiDangForm(forms.ModelForm):
    class Meta:
        model = BaiDang
        fields = '__all__'