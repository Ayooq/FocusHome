# Generated by Django 2.2.2 on 2019-07-12 10:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('DeviceUnits', '0010_auto_20190705_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='units',
            name='comment',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
