# Generated by Django 2.2.2 on 2019-07-02 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Profiles', '0003_auto_20190701_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profiles',
            name='role',
            field=models.ForeignKey(default=None, on_delete=models.SET(0), to='auth.Group'),
        ),
    ]