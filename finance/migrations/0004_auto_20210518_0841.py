# Generated by Django 3.2 on 2021-05-18 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_auto_20210504_0140'),
    ]

    operations = [
        migrations.AddField(
            model_name='hoadonchuoikham',
            name='thoi_gian_thanh_toan',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hoadonlamsang',
            name='thoi_gian_thanh_toan',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='hoadonthuoc',
            name='thoi_gian_thanh_toan',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]