# from django.db import models
# from Devices.models import Devices
#
#
# class Family(models.Model):
#     name = models.CharField(
#         max_length=255,
#         blank=False,
#         null=False,
#     )
#     title = models.CharField(
#         max_length=255,
#         blank=True,
#         null=True,
#         default=""
#     )
#     comment = models.TextField(
#         blank=True,
#         null=True,
#         default=""
#     )
#
#     class Meta:
#         db_table = 'units_family'
#
#     def __str__(self):
#         return self.name
#
#
# class Units(models.Model):
#     family = models.ForeignKey(
#         Family,
#         on_delete=models.CASCADE,
#         default=None
#     )
#
#     name = models.CharField(
#         max_length=255,
#         blank=False,
#         null=False,
#     )
#     title = models.CharField(
#         max_length=255,
#         blank=True,
#         null=True,
#         default=""
#     )
#     is_custom = models.BooleanField(
#         blank=False,
#         null=False,
#         default=True
#     )
#     is_pin = models.BooleanField(
#         blank=False,
#         null=False,
#         default=True
#     )
#     comment = models.TextField(
#         blank=True,
#         null=True,
#         default=""
#     )
#     format = models.TextField(
#         blank=True,
#         null=True,
#         default=None
#     )
#
#     class Meta:
#         db_table = 'units'
#
#     def __str__(self):
#         return self.name + (' (' + self.title + ')' if self.title else "")
#
#
# class ClientUnits(models.Model):
#     device = models.ForeignKey(
#         Devices,
#         on_delete=models.CASCADE,
#         default=None
#     )
#     unit = models.ForeignKey(
#         Units,
#         on_delete=models.CASCADE,
#         default=None
#     )
#
#     state = models.TextField(
#         blank=True,
#         null=True,
#         default="{}"
#     )
#     comment = models.TextField(
#         max_length=255,
#         blank=True,
#         null=True,
#         default=""
#     )
#
#     def __str__(self):
#         return "{}:{}".format(self.device.uid, self.unit.name)
#
#
# class GPIOConfig(models.Model):
#     device = models.ForeignKey(
#         Devices,
#         on_delete=models.CASCADE,
#         default=None
#     )
#     unit = models.ForeignKey(
#         Units,
#         on_delete=models.CASCADE,
#         default=None
#     )
#
#     pin = models.SmallIntegerField(
#         max_length=3,
#         blank=True,
#         null=True,
#         default=None
#     )
#     description = models.CharField(
#         max_length=255,
#         blank=True,
#         null=True,
#         default=""
#     )
#     format = models.TextField(
#         blank=True,
#         null=True,
#         default=None
#     )
#
#     class Meta:
#         db_table = 'devices_config'
#
#     @staticmethod
#     def create_yaml():
#         pass
#
#
# def getPins():
#     return list(range(0, 31))
#
