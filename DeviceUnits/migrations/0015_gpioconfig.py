# Generated by Django 2.2.2 on 2019-07-12 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Devices', '0004_devices_uid'),
        ('DeviceUnits', '0014_auto_20190712_1046'),
    ]

    operations = [
        migrations.CreateModel(
            name='GPIOConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pin', models.SmallIntegerField(default=None, max_length=3)),
                ('description', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('format', models.TextField(blank=True, default='{}', null=True)),
                ('device', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='Devices.Devices')),
                ('unit', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='DeviceUnits.Units')),
            ],
        ),
    ]
