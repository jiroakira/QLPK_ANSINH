from import_export import resources
from .models import DichVuKham

class DichVuKhamResource(resources.ModelResource):
    class Meta:
        model = DichVuKham
        