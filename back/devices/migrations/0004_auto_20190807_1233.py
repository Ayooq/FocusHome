# Generated by Django 2.2.3 on 2019-08-07 06:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0003_auto_20190801_1251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='config',
            name='format',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
    ]
