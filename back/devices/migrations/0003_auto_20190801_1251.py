# Generated by Django 2.2.3 on 2019-08-01 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0002_auto_20190726_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='format',
            field=models.TextField(blank=True, null=True),
        ),
    ]