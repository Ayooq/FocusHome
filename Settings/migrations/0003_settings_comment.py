# Generated by Django 2.2.2 on 2019-07-04 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Settings', '0002_settings_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='comment',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
    ]