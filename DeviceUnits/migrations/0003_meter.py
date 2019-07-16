# Generated by Django 2.2.2 on 2019-07-04 11:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('DeviceUnits', '0002_auto_20190704_1106'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('value', models.CharField(max_length=255)),
                ('comment', models.TextField(blank=True, default='', max_length=255, null=True)),
                ('family', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='DeviceUnits.Family')),
            ],
        ),
    ]