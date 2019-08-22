from clients.models import Client
from django.contrib.auth.models import Group, User
from django.db import models


class Profile(models.Model):
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        default=None,
    )
    role = models.ForeignKey(
        Group,
        on_delete=models.SET(0),
        default=2,
    )
    auth = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=None,
    )

    class Meta:
        db_table = 'profiles'
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.firstname + ' ' + self.lastname
