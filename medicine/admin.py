from medicine.models import BaoHiemThuoc, ChiTietThuoc, CongTy, DonThuoc, GiaThuoc, KeDonThuoc, NhomThau, Thuoc, ThuocLog, TrangThaiDonThuoc, VatTu
from django.contrib import admin

class ThuocAdmin(admin.ModelAdmin):
    search_fields = ('ten_thuoc',)

admin.site.register(Thuoc, ThuocAdmin)
admin.site.register(DonThuoc)
admin.site.register(TrangThaiDonThuoc)
admin.site.register(KeDonThuoc)
admin.site.register(ThuocLog)
admin.site.register(ChiTietThuoc)
admin.site.register(CongTy)
admin.site.register(GiaThuoc)
admin.site.register(BaoHiemThuoc)
admin.site.register(NhomThau)
admin.site.register(VatTu)