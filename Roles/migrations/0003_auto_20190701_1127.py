# Generated by Django 2.2.2 on 2019-07-01 11:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Roles', '0002_auto_20190701_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roles',
            name='group_name',
            field=models.IntegerField(choices=[(1, 'Управление'), (2, 'Клиенты')], default=2),
        ),
    ]
