from django.db import models
from django.db import connection
import Django.util as util
import json


class Monitoring(models.Model):


    @staticmethod
    def get_devices_list(request, **kwargs):
        VALUES_ELSE_NAME = 'иначе'

        where = ""
        device_id = util.toInt(request.GET.get('device_id', 0))
        client_id = util.toInt(request.GET.get('client_id', 0))

        if device_id > 0:
            where += " and dt.id="+str(device_id)
        if client_id > 0:
            where += " and dt.client_id="+str(client_id)

        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                dt.id as id,
                dt.name as name,
                dt.address as address,
                dt.id as uid,
                ct.id as client__id,
                ct.name as client__name,
                DATE_FORMAT(ds.`timestamp`, "%d.%m.%Y %H:%i:%s") as `date`, 
                duf.name as family,
                duu.name as unit,
                dug.id as unit__id,
                duu.title as annotation,
                ds.state,
                duu.format as duu_format,
                get_unit_format(
                    COALESCE(dug.format, duu.format),
                    ds.state
                ) as unit_format
            from devices as dt
                inner join clients as ct
                    on ct.id = dt.client_id
                inner join devices_config as dug
                    on dug.device_id = dt.id
                inner join units as duu
                    on duu.id = dug.unit_id
                inner join units_family as duf
                    on duf.id = duu.family_id
                inner join status as ds
                    on ds.unit_id = dug.id
            where (1)
                """ + (" and d.client_id = %(client_id)s" if request.user.role_code == 'clients' else '') + """
                {where}
            ORDER by dt.id, duu.family_id
            """.format(
                where=where
            )
        )
        devices_list = util.dictfetchall(cursor)
        cursor.close()
        devices_list = devices_list if devices_list is not None else []

        devices = {}
        for dev in devices_list:
            device_id = dev['id']

            if not device_id in devices:
                devices[device_id] = {
                    'id': device_id,
                    'name': dev['name'],
                    'address': dev['address'],
                    'uid': dev['uid'],
                    'client__id': dev['client__id'],
                    'client__name': dev['client__name'],
                    'status': {}
                }

            if not dev['family'] in devices[device_id]['status']:
                devices[device_id]['status'][dev['family']] = {}

            if dev['family'] is not None:
                # unit_value = str(dev.get("state",""))
                # state_format = json.loads(dev['state_format']) if util.is_json(dev['state_format']) else {}
                # state_format_values = state_format.get("values", [])
                # state_format_values_else = {}
                # state_format_value_index = {}
                # controlValues = []
                # for format_value in state_format_values:
                #     if str(format_value['value']) == unit_value:
                #         state_format_value_index = format_value
                #         if format_value['value'] != VALUES_ELSE_NAME:
                #             controlValues.append(format_value['value'])
                #         else:
                #             state_format_values_else = format_value
                #
                # unit_format = {
                #     "title": state_format.get("title", dev['annotation']),
                #     "chart": state_format.get("chart", None),
                #     "controls": state_format.get("controls", []),
                #     "controlValues": controlValues
                # }
                #
                # unit_format__type = state_format.get("type", "")
                # if unit_format__type == "INTEGER":
                #     unit_format["value"] = util.toInt(unit_value)
                #     unit_format["caption"] = state_format_value_index.get("title", unit_value)
                #     unit_format["class"] = state_format_value_index.get("class", "")
                # elif unit_format__type == "STRING":
                #     unit_format["value"] = unit_value
                #     unit_format["caption"] = state_format_value_index.get("title", unit_value)
                #     unit_format["class"] = state_format_value_index.get("class", "")
                # elif unit_format__type == "FLOAT_RANGE":
                #     unit_value_float = util.toFloat(unit_value)
                #     unit_format["value"] = unit_value_float
                #     unit_format["caption"] = state_format.get("format", "{0:.2f}").format(util.toFloat(unit_value)).replace('.',',')
                #     unit_format["class"] = state_format_values_else.get("class", "")
                #     for item in state_format_values:
                #         if not item['value'] == VALUES_ELSE_NAME:
                #             keyTuple = util.strRangeToTuple(item['value'])
                #             if keyTuple[0] <= unit_value_float < keyTuple[1]:
                #                 unit_format["class"] = item.get("class", "")
                #                 break
                # else:
                #     unit_format["value"] = unit_value
                #     unit_format["caption"] = unit_value
                #     unit_format["class"] = "bd bdc-brown-100 bg-light text-dark"

                devices[device_id]['status'][dev['family']][dev['unit']] = {
                    'date': dev['date'],
                    'unit': dev['unit'],
                    'unit__id': dev['unit__id'],
                    'annotation': dev['annotation'],
                    'state': dev['state'],
                    'unit_format': util.toJson(dev['unit_format']),
                }

        del devices_list

        return devices
