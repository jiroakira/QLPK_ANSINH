from clinic.serializers import ChuoiKhamSerializerSimple
from django.db import models
from finance.models import HoaDonChuoiKham, HoaDonThuoc
from rest_framework import serializers

class HoaDonChuoiKhamSerializer(serializers.ModelSerializer):
    chuoi_kham = ChuoiKhamSerializerSimple()
    class Meta:
        model = HoaDonChuoiKham
        fields = '__all__'

class HoaDonThuocSerializer(serializers.ModelSerializer):
    class Meta:
        model = HoaDonThuoc
        fields = '__all__'

# TODO Có thể custom lại serializer của 2 bảng HoaDonChuoiKham và HoaDonThuoc