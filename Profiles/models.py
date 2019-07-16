from django.db import models
from django.contrib.auth.models import User, Group, Permission
from Clients.models import Clients


class Profiles(models.Model):
    firstname = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    lastname = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    phone = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    role = models.ForeignKey(
        Group,
        on_delete=models.SET(0),
        default=2
    )

    client = models.ForeignKey(
        Clients,
        on_delete=models.CASCADE,
        default=None
    )
    auth = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=None
    )

    def __str__(self):
        return self.firstname + " " + self.lastname