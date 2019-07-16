from django.db import models
from Clients.models import Clients
import Django.util as util
import json
import re


class Devices(models.Model):
    uid = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=""
    )
    comment = models.TextField(
        blank=True,
        null=True,
        default=""
    )

    client = models.ForeignKey(
        Clients,
        on_delete=models.CASCADE,
        default=None
    )

    def __str__(self):
        return "[{}] {}".format(self.uid, self.name)

    @staticmethod
    def unitValidate(unit_text):
        if not util.is_json(unit_text):
            return "not valid JSON"

        unit_dict = json.loads(unit_text)

        if type(unit_dict) != dict:
            return 'описание датчика должно быть JSON объектом'

        unit_type = unit_dict.get("type", "STRING")
        if not unit_type in ("STRING", "INTEGER", "FLOAT_RANGE"):
            return 'поле "type" должно быть одним из: "STRING", "INTEGER", "FLOAT_RANGE"'

        unit_chart = unit_dict.get("chart", None)
        if not unit_chart in (None, "line", "area"):
            return 'поле "chart" должно быть одним из: "line", "area" или отсутствовать'

        unit_control = unit_dict.get("control", None)
        if unit_type in ("STRING", "INTEGER"):
            if not unit_control in (None, "toggle"):
                return 'поле "control" должно быть одним из: "toggle" или отсутствовать'

        unit_values = unit_dict.get("values", {})
        if type(unit_values) != dict:
            return 'поле "values" должно быть JSON объектом'
        if len(unit_values.keys()) == 0:
            return 'добавьте хотя бы одно значение в поле "values"'

        if not "else" in unit_values:
            return 'поле "values" должно содержать значение по умолчанию с ключом "else"'

        if unit_type in ("INTEGER"):
            for key in list(filter(lambda x: x!='else', list(unit_values.keys()))):
                if not key.isdigit():
                    return 'поле "values", значение '+str(key)+' должно содержать только цифры'
        if unit_type in ("STRING"):
            pass
        if unit_type in ("FLOAT_RANGE"):
            for key in list(filter(lambda x: x!='else', list(unit_values.keys()))):
                if not re.search(r"\-?\d+\.\.\-?\d+", key):
                    return 'поле "values", значение '+str(key)+' должно быть в формате "\-?\d+\.\.\-?\d+"'

        for key in unit_values:
            if type(unit_values[key]) != dict:
                return 'поле "values", значение ' + str(key) + ' должно быть JSON объектом'



        return 1
