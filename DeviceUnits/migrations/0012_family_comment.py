# Generated by Django 2.2.2 on 2019-07-12 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DeviceUnits', '0011_units_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='comment',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]