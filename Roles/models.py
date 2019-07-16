from django.db import models


class Group(models.Model):
    id = models.IntegerField(
        blank=False,
        null=False,
        primary_key=True,
        unique=True
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.name

class Roles(models.Model):
    id = models.IntegerField(
        blank=False,
        null=False,
        primary_key=True,
        unique=True
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        default=2
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    @property
    def full_name(self):
        role = Group.objects.get(pk=self.group_id)

        return self.name + " (" + role.name + ")"

    def __str__(self):
        return self.full_name
