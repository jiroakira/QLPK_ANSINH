from django.apps import AppConfig

class ClinicConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'clinic'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('User'))
        registry.register(self.get_model('ChuoiKham'))
        registry.register(self.get_model('PhanKhoaKham'))
        registry.register(self.get_model('DichVuKham'))
        registry.register(self.get_model('KetQuaTongQuat'))
        registry.register(self.get_model('KetQuaChuyenKhoa'))
        registry.register(self.get_model('MauPhieu'))
        registry.register(self.get_model('BaiDang'))
        registry.register(self.get_model('LichHenKham'))
        registry.register(self.get_model('BacSi'))
        registry.register(self.get_model('PhongChucNang'))
        registry.register(self.get_model('ChiSoXetNghiem'))
        registry.register(self.get_model('KetQuaXetNghiem'))
        registry.register(self.get_model('HtmlKetQua'))
        
