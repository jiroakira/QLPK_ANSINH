# Generated by Django 3.2 on 2021-05-01 07:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clinic', '0003_lichhenkham_thanh_toan_sau'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chuoikham',
            name='lich_hen',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='danh_sach_chuoi_kham', to='clinic.lichhenkham'),
        ),
        migrations.AlterField(
            model_name='lichhenkham',
            name='loai_dich_vu',
            field=models.CharField(blank=True, choices=[('kham_chua_benh', 'Khám Chữa Bệnh'), ('kham_suc_khoe', 'Khám Sức Khỏe'), ('kham_theo_yeu_cau', 'Khám Theo Yêu Cầu')], max_length=25, null=True),
        ),
    ]
