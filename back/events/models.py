# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Event(models.Model):
    unit = models.ForeignKey('devices.Config', models.DO_NOTHING)
    type = models.ForeignKey('msg_types.Message', models.DO_NOTHING)
    timestamp = models.DateTimeField()
    message = models.CharField(max_length=8)

    class Meta:
        managed = False
        db_table = 'events'