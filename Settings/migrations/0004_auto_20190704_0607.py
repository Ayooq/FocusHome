# Generated by Django 2.2.2 on 2019-07-04 06:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Settings', '0003_settings_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='comment',
            field=models.CharField(blank=True, default=None, max_length=255, null=True),
        ),
    ]