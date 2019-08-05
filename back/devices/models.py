import json
import re

import yaml
from django.db import connection, models

from clients.models import Client
from units.models import Unit


class Device(models.Model):
    name = models.CharField(max_length=8, blank=True)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='device',
    )
    address = models.CharField(max_length=255, blank=True)
    comment = models.TextField(blank=True)

    class Meta:
        db_table = 'devices'
        verbose_name = 'Устройство'
        verbose_name_plural = 'Устройства'

    def __str__(self):
        return self.name

    @staticmethod
    def validate(format_str):
        try:
            unit_config = json.loads(format_str)
        except ValueError:
            return 'JSON сформирован неправильно!'

        if not isinstance(unit_config, dict):
            return 'Убедитесь в том, что формат задан верно. ' \
                'Он должен быть выполнен в виде словаря.'

        unit_type = unit_config.get('type', 'STRING')
        unit_chart = unit_config.get('chart')
        unit_control = unit_config.get('control')

        if unit_type not in ('STRING', 'INTEGER', 'FLOAT_RANGE'):
            return 'Поле "type" должно быть заполнено одним из значений: ' \
                '"STRING", "INTEGER", "FLOAT_RANGE".'
        elif unit_chart not in ('line', 'area', '', None):
            return 'Поле "chart" должно быть либо с одним из значений ' \
                '"line", "area", либо незаполненным.'
        elif unit_control not in ('toggle', '', None):
            return 'Поле "control" должно быть либо со значением ' \
                '"toggle", либо незаполненным.'

        unit_values = unit_config.get('values', {})

        if not isinstance(unit_values, dict):
            return 'Поле "values" должно содержать словарь значений.'
        elif not unit_values.keys():
            return 'Добавьте хотя бы одно значение в поле "values".'
        elif 'else' not in unit_values:
            return 'Поле "values" должно содержать значение по умолчанию ' \
                'с ключом "else".'

        for value in unit_values.values():
            if not isinstance(value, dict):
                return 'Значения в поле "values" должны быть JSON-объектами.'

        if unit_type in ('INTEGER'):
            for key in filter(
                lambda x: x != 'else', unit_values
            ):
                if not key.isdigit():
                    return 'Поле "values" должно содержать только числа.'
        elif unit_type in ('FLOAT_RANGE'):
            for key in filter(
                lambda x: x != 'else', unit_values
            ):
                if key != str(float(key)):
                    return 'Значения в поле "values" должны быть в формате ' \
                        'десятичной дроби.'


class Config(models.Model):
    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name='config',
    )
    unit = models.ForeignKey(
        Unit,
        on_delete=models.CASCADE,
        related_name='config'
    )
    pin = models.SmallIntegerField(null=True)
    format = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Конфигурация'
        verbose_name_plural = 'Настройки'

    @staticmethod
    def form_json(device_id):
        config = Config.objects \
            .select_related('unit', 'unit__family', ) \
            .filter(device_id=device_id) \
            .values_list('unit__family__name', 'unit__name', 'pin', 'format')

        return json.dumps([json.dumps(unit) for unit in config])
