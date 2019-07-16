from django.db import models
from Clients.models import Clients
import re


class Groups(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.name


class Types(models.Model):
    type = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        primary_key=True
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.name


class Settings(models.Model):
    group = models.ForeignKey(
        Groups,
        on_delete=models.CASCADE,
        default=None
    )

    code = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        unique=True
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    type = models.ForeignKey(
        Types,
        on_delete=models.CASCADE,
        default=None
    )
    value = models.TextField(
        blank=False,
        null=False
    )
    comment = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None
    )


    def __str__(self):
        return "{} ({}=({}){})".format(self.name, self.code, self.type_id, self.value if len(self.value)<20 else self.value[:20]+"...")

    @staticmethod
    def get(code=()):
        list = {}
        if len(code)>0:
            items = Settings.objects.filter(code__in=code).values('code','value','type_id')
            for item in items:
                list[item['code']] = item['value']

        return list

    @staticmethod
    def all(request, group_id=0):
        list = {
            'app': {
                'name': Settings.objects.filter(code='app_name')[0].value
            },
            'clients': Clients.get_clients_list(request),
            'group': {}
        }
        if group_id > 0:
            group_set = Settings.objects.filter(group_id=group_id).values('code','value','type_id')
            group_dict = {}
            if group_set is not None:
                regex = re.compile('(\n|$\s+)')
                for r in group_set:
                    r['value'] = re.sub(regex,'',r['value'])
                    group_dict[r['code']] = r
            del group_set
            list['group'] = group_dict

        return list
