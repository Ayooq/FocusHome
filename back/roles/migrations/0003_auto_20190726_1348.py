# Generated by Django 2.2.3 on 2019-07-26 07:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('roles', '0002_auto_20190726_1129'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='role',
            options={'verbose_name': 'Роль', 'verbose_name_plural': 'Роли'},
        ),
    ]