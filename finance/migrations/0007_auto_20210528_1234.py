# Generated by Django 3.2 on 2021-05-28 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_auto_20210528_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hoadonchuoikham',
            name='thoi_gian_cap_nhat',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='hoadonchuoikham',
            name='thoi_gian_tao',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
