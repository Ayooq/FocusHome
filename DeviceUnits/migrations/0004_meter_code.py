# Generated by Django 2.2.2 on 2019-07-04 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DeviceUnits', '0003_meter'),
    ]

    operations = [
        migrations.AddField(
            model_name='meter',
            name='code',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]