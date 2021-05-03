from django.apps import AppConfig


class MedicineConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'
    name = 'medicine'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Thuoc'))
        registry.register(self.get_model('KeDonThuoc'))
        registry.register(self.get_model('DonThuoc'))
        registry.register(self.get_model('VatTu'))
        registry.register(self.get_model('KeVatTu'))
        registry.register(self.get_model('CongTy'))