import re

from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=16)

    class Meta:
        db_table = 'config_groups'
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.name


class Datatype(models.Model):
    type = models.CharField(max_length=16)
    name = models.CharField(max_length=16)

    class Meta:
        db_table = 'config_datatypes'
        verbose_name = 'Тип данных'
        verbose_name_plural = 'Типы данных'

    def __str__(self):
        return self.name


class Configuration(models.Model):
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
    )
    datatype = models.ForeignKey(
        Datatype,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=80)
    code = models.CharField(max_length=40, unique=True)
    comment = models.CharField(max_length=80, blank=True)
    value = models.CharField(max_length=16)

    class Meta:
        db_table = 'config'
        verbose_name = 'Конфигурация'
        verbose_name_plural = 'Настройки'

    def __str__(self):
        return '{} ({}=<{}:{}>) '.format(
            self.name,
            self.code,
            self.datatype.type,
            self.value,
        )

    @staticmethod
    def fetch_settings(request=None, code=()):
        if code:
            dict_ = {}
            entries = Configuration.objects.filter(code__in=code)

            for entry in entries.values('code', 'value'):
                dict_[entry['code']] = entry['value']

            return dict_

        elif request:
            from clients.models import Client

            dict_ = {
                'app': {
                    'name': Configuration.objects.get(code='app_name').value
                },
                'clients': Client.get_clients(request),
            }

            group_id = request.GET.get('group_id', 0)
            entries = Configuration.objects.filter(group=group_id)

            if entries:
                dict_['group'] = {}
                pattern = re.compile(r'(\n|\s+$)')

                for entry in entries.values('code', 'value', 'datatype__type'):
                    code = entry.pop('code')
                    entry['value'] = re.sub(pattern, '', entry['value'])
                    dict_['group'][code] = entry

            return dict_
