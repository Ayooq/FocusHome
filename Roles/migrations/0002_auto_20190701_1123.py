# Generated by Django 2.2.2 on 2019-07-01 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Roles', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='roles',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False, unique=True),
        ),
    ]
