from django.db import models
from Devices.models import Devices
from Profiles.models import Profiles
from Clients.models import Clients
from django.db import connection
import Django.util as util
import json


class Monitoring(models.Model):

    @staticmethod
    def get_devices_list(request, **kwargs):
        user_auth = Profiles.objects.get(auth_id=request.user.id)

        where = ""
        if request.user.is_superuser == 1:
            client_id = request.GET.get('client_id', '')
            client_id = int(client_id) if client_id.isdigit() else 0
            if client_id > 0:
                    where += " and ct.id=" + str(client_id)
        else:
            where += " and ct.id=" + str(user_auth.client_id)

        device_id = request.GET.get('device_id', False)
        if device_id:
            if device_id.isdigit():
                where += " and dt.id="+str(device_id)

        cursor = connection.cursor()
        cursor.execute("""
            SELECT
                dt.id as id,
                dt.name as name,
                dt.address as address,
                dt.uid as uid,
                ct.id as client__id,
                ct.name as client__name,
                DATE_FORMAT(ds.`timestamp`, "%d.%m.%Y %H:%i:%s") as `date`, 
                duf.name as family,
                duu.name as unit,
                dug.id as unit__id,
                duu.title as annotation,
                ds.state,
                COALESCE(dug.format, duu.format, "{{}}") as state_format
            from {devices_table} as dt
                inner join {clients_table} as ct
                    on ct.id = dt.client_id
                inner join DeviceUnits_gpioconfig as dug
                    on dug.device_id = dt.id
                inner join DeviceUnits_units as duu
                    on duu.id = dug.unit_id
                inner join DeviceUnits_family as duf
                    on duf.id = duu.family_id
                inner join status as ds
                    on ds.unit_id = dug.id
            where (1)
                {where}
            ORDER by dt.id, duu.family_id
            """.format(
                devices_table=Devices._meta.db_table,
                clients_table=Clients._meta.db_table,
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
                unit_value = str(dev.get("state",""))
                state_format = json.loads(dev['state_format']) if util.is_json(dev['state_format']) else {}
                state_format_values = state_format.get("values", {})
                state_format_value_index = state_format_values.get(unit_value, state_format_values.get("else", {}))

                unit_format = {
                    "title": state_format.get("title", dev['annotation']),
                    "chart": state_format.get("chart", None),
                    "control": state_format.get("control", None),
                    "controlValues": list(filter(lambda x : x != 'else', list(state_format_values.keys())))
                }

                unit_format__type = state_format.get("type", "")
                if unit_format__type == "INTEGER":
                    unit_format["value"] = util.toInt(unit_value)
                    unit_format["caption"] = state_format_value_index.get("title", unit_value)
                    unit_format["class"] = state_format_value_index.get("class", "")
                elif unit_format__type == "STRING":
                    unit_format["value"] = unit_value
                    unit_format["caption"] = state_format_value_index.get("title", unit_value)
                    unit_format["class"] = state_format_value_index.get("class", "")
                elif unit_format__type == "FLOAT_RANGE":
                    unit_value_float = util.toFloat(unit_value)
                    unit_format["value"] = unit_value_float
                    unit_format["caption"] = state_format.get("format", "{0:.2f}").format(util.toFloat(unit_value)).replace('.',',')
                    unit_format["class"] = state_format_values.get("else", {}).get("class", "")
                    for key in state_format_values:
                        if not key == "else":
                            keyTuple = util.strRangeToTuple(key)
                            if keyTuple[0] <= unit_value_float < keyTuple[1]:
                                unit_format["class"] = state_format_values[key].get("class", "")
                                break
                else:
                    unit_format["value"] = unit_value
                    unit_format["caption"] = unit_value
                    unit_format["class"] = "bd bdc-brown-100 bg-light text-dark"



                devices[device_id]['status'][dev['family']][dev['unit']] = {
                    'date': dev['date'],
                    'unit': dev['unit'],
                    'unit__id': dev['unit__id'],
                    'annotation': dev['annotation'],
                    'state': dev['state'],
                    'unit_format': unit_format,
                }

        del devices_list

        return devices
