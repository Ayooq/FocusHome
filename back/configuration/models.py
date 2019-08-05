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
    def get(code=''):
        dict_ = {}

        if code:
            entries = Configuration.objects.filter(code=code)

            for e in entries.values('code', 'value'):
                dict_[e['code']] = e['value']

        return dict_

    @staticmethod
    def all(request):
        from clients.models import Client

        dict_ = {
            'app': {
                'name': Configuration.objects.get(code='app_name').value
            },
            'clients': Client.get_clients(request),
        }

        group_id = request.GET.get('group_id')

        if group_id:
            dict_['group'] = {}
            entries = Configuration.objects.filter(group=group_id) \
                .values('code', 'value')

            if entries:
                pattern = re.compile(r'(\n|\s+$)')

                for e in entries:
                    e['value'] = re.sub(pattern, '', e['value'])
                    dict_['group'][e['code']] = e['value']

        return dict_
