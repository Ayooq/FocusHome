# Generated by Django 2.2.2 on 2019-07-15 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DeviceUnits', '0018_auto_20190715_0806'),
    ]

    operations = [
        migrations.AddField(
            model_name='units',
            name='is_pin',
            field=models.BooleanField(default=True),
        ),
    ]