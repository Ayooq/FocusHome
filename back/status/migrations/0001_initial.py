# Generated by Django 2.2.3 on 2019-08-23 09:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('devices', '0004_auto_20190807_1233'),
    ]

    operations = [
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('state', models.CharField(max_length=8)),
                ('unit', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='devices.Config', unique=True)),
            ],
            options={
                'db_table': 'status',
            },
        ),
    ]
