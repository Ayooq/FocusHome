from django.db import models
# from Clients.models import Clients
import Django.util as util
import json
import re
from django.http import JsonResponse
from django.db import connection
from Django.models import BaseModel


# class Devices(models.Model):
#     # uid = models.CharField(
#     #     max_length=255,
#     #     blank=False,
#     #     null=False
#     # )
#     name = models.CharField(
#         max_length=255,
#         blank=False,
#         null=False
#     )
#     address = models.CharField(
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
#     client = models.ForeignKey(
#         Clients,
#         on_delete=models.CASCADE,
#         default=None
#     )
#
#     class Meta:
#         db_table = 'devices'
#
#     def __str__(self):
#         return "[{}] {}".format(self.uid, self.name)
#
#     @staticmethod
#     def unitValidate(unit_text):
#         if not util.is_json(unit_text):
#             return "not valid JSON"
#
#         unit_dict = json.loads(unit_text)
#
#         if type(unit_dict) != dict:
#             return 'описание датчика должно быть JSON объектом'
#
#         unit_type = unit_dict.get("type", "STRING")
#         if not unit_type in ("STRING", "INTEGER", "FLOAT_RANGE"):
#             return 'поле "type" должно быть одним из: "STRING", "INTEGER", "FLOAT_RANGE"'
#
#         unit_chart = unit_dict.get("chart", None)
#         if not unit_chart in (None, "line", "area"):
#             return 'поле "chart" должно быть одним из: "line", "area" или отсутствовать'
#
#         unit_control = unit_dict.get("control", None)
#         if unit_type in ("STRING", "INTEGER"):
#             if not unit_control in (None, "toggle"):
#                 return 'поле "control" должно быть одним из: "toggle" или отсутствовать'
#
#         unit_values = unit_dict.get("values", {})
#         if type(unit_values) != list:
#             return 'поле "values" должно быть JSON объектом'
#         if len(unit_values) == 0:
#             return 'добавьте хотя бы одно значение в поле "values"'
#
#         if not "иначе" in unit_values:
#             return 'поле "values" должно содержать значение по умолчанию с ключом "иначе"'
#
#         for item in unit_values:
#             if type(item) != dict:
#                 return 'поле "values", значение ' + str(item.get('value', '')) + ' должно быть JSON объектом'
#
#         if unit_type in ("INTEGER"):
#             for item in list(filter(lambda x: x.get('value') != 'иначе', unit_values)):
#                 value = str(item.get('value',''))
#                 if not value.isdigit():
#                     return 'поле "values", значение ' + value + ' должно содержать только цифры'
#         if unit_type in ("STRING"):
#             pass
#         if unit_type in ("FLOAT_RANGE"):
#             for item in list(filter(lambda x: x.get('value') != 'иначе', unit_values)):
#                 value = str(item.get('value', ''))
#                 if not re.search(r"\-?\d+\.\.\-?\d+", value):
#                     return 'поле "values", значение ' + value + ' должно быть в формате "\-?\d+\.\.\-?\d+"'
#
#         return 1


class Device(BaseModel):
    def get(self):
        if self.id:
            query = """
                SELECT
                      d.id as device_id
                    , d.name as device_name
                    , d.address as device_address
                    , d.comment as device_comment
                    , d.client_id as device_client_id
                    , d.snmp_host
                    , d.snmp_community
                    , d.snmp_version
                    , d.snmp_user
                    , d.snmp_password
                FROM devices as d
                WHERE d.id=%(device_id)s
            """
            self.cursor.execute(query, {
                "device_id": self.id
            })
            self.data = util.dictfetchone(self.cursor)
        else:
            self.data = {
                "device_id": 0,
                "device_name": "Назначается автоматически",
                "device_address": "",
                "device_comment": "",
                "device_client_id": 0,
                "snmp_host": "",
                "snmp_community": "",
                "snmp_version": "",
                "snmp_user": "",
                "snmp_password": "",
            }


        return self.data

    def get_units(self, gpio_format='str', is_gpio=1):
        is_gpio = -1

        query = """
            select
                COALESCE(dug.src_id,"") as src_id,
                COALESCE(src.name,"") as units__src,
                duf.name as family__name,
                duf.title as family__title,
                duu.id as units__id,
                duu.name as units__name,
                duu.title as units__title,
                duu.is_gpio as is_pin,
                dug.id as gpio__id,
                COALESCE(dug.pin, -1) as gpio__pin,
                COALESCE(dug.format, duu.format, "{}") as gpio__format
            from devices as dt
                inner join units as duu
                    """ + ("on duu.is_gpio=1" if is_gpio == 1 else "") + """
                inner join units_family as duf
                    on duf.id = duu.family_id
                left join devices_config as dug
                    on dug.device_id = dt.id
                    and dug.unit_id = duu.id
                left join units as src
                    on src.id = dug.src_id
            where dt.id=%(device_id)s
            order by duf.name, duu.name
        """

        self.cursor.execute(query, {
            'device_id': self.device_id if self.device_id > 0 else -1
        })

        units = util.dictfetchall(self.cursor)

        if gpio_format == 'json':
            for index,item in enumerate(units):
                if util.is_json(item['gpio__format']):
                    units[index]['gpio__format'] = util.toJson(item['gpio__format'])
                else:
                    units[index]['gpio__format'] = {
                        "title": "",
                        "type": "INTEGER",
                        "chart": "",
                        "controls": [],
                        "values": [
                            {
                                "value": "иначе",
                                "title": "Неизвестно",
                                "class": "bg-light text-dark"
                            }
                        ]
                    }

                if not 'is_default' in units[index]['gpio__format']:
                    units[index]['gpio__format']['is_default'] = True

        return units

    # def get_aliases(self):
    #     aliases = {}
    #
    #     query = """
    #         select
    #               dca.id
    #             , dca.name
    #             , dca.title
    #         from devices_config_aliases as dca
    #         order by dca.title
    #     """
    #
    #     self.cursor.execute(query)
    #
    #     return util.dictfetchall(self.cursor)

    def get_pins(self):
        return list(range(0, 31))

    @staticmethod
    def get_monitoring_gpio_types():
        return [
            {'name': "STRING", 'desc': 'строка'},
            {'name': "INTEGER", 'desc': 'целое'},
            {'name': "FLOAT_RANGE", 'desc': 'массив дробных чисел'}
        ]

    @staticmethod
    def get_monitoring_chart_types():
        return [
            {'name': "spline", 'desc': 'линейный'},
            {'name': "area", 'desc': 'столбчатый'}
        ]

    @staticmethod
    def get_monitoring_controls():
        return [
            {'name': "toggle", 'desc': 'переключатель'},
        ]

    @staticmethod
    def get_monitoring_widget_formats():
        return [
            {'name': "bg-light text-dark", 'desc': 'светло-серый'},
            {'name': "bg-secondary text-white", 'desc': 'темно-серый'},
            {'name': "bg-success text-white", 'desc': 'зеленый'},
            {'name': "bg-warning text-white", 'desc': 'желтый'},
            {'name': "bg-danger text-white", 'desc': 'красный'},
        ]

    @staticmethod
    def unitValidate(unit_dict, unit_name=''):
        if type(unit_dict) != dict:
            return unit_name+ '. описание датчика должно быть JSON объектом'

        if bool(unit_dict.get('is_default',True)):
            return 1

        unit_type = unit_dict.get("type", "STRING")
        if not unit_type in ("STRING", "INTEGER", "FLOAT_RANGE"):
            return unit_name+ '. поле "type" должно быть одним из: "STRING", "INTEGER", "FLOAT_RANGE"'

        unit_chart = unit_dict.get("chart", None)
        if not unit_chart in (None, "", "spline", "area"):
            return unit_name+ '. поле "chart" должно быть одним из: "line", "area" или отсутствовать'

        unit_controls = unit_dict.get("controls", [])
        if unit_type in ("STRING", "INTEGER"):
            for cntrl in unit_controls:
                if not cntrl in (None, "toggle"):
                    return unit_name+ '. поле "control" должно быть одним из: "toggle" или отсутствовать'

        unit_values = unit_dict.get("values", {})
        if type(unit_values) != list:
            return 'поле "values" должно быть JSON объектом'
        if len(unit_values) == 0:
            return unit_name+ '. добавьте хотя бы одно значение в поле "values"'

        is_else = False
        for item in unit_values:
            if item.get('value') == 'иначе':
                is_else = True
                break
        if is_else == False:
            return unit_name + '. поле "values" должно содержать значение по умолчанию с ключом "иначе"'

        for item in unit_values:
            if type(item) != dict:
                return unit_name+ '. поле "values", значение ' + str(item.get('value', '')) + ' должно быть JSON объектом'

        if unit_type in ("INTEGER"):
            for item in list(filter(lambda x: x.get('value') != 'иначе', unit_values)):
                value = str(item.get('value',''))
                if not value.isdigit():
                    return unit_name+ '. поле "values", значение ' + value + ' должно содержать только цифры'
        if unit_type in ("STRING"):
            pass
        if unit_type in ("FLOAT_RANGE"):
            for item in list(filter(lambda x: x.get('value') != 'иначе', unit_values)):
                value = str(item.get('value', ''))
                if not re.search(r"\-?\d+\.\.\-?\d+", value):
                    return unit_name+ '. поле "values", значение ' + value + ' должно быть в формате "-1000..1000"'

        return 1
