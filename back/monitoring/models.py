import json

from clients.models import Client
from devices.models import Config, Device
from django.db import connection, models
from focus import utils
from profiles.models import Profile
from units.models import Family, Unit


class Monitor(models.Model):

    @staticmethod
    def get_devices_dict(request):
        tail = ''

        if request.user.is_superuser:
            client_id = request.GET.get('client_id', '')

            if client_id.isdigit() and int(client_id) > 0:
                tail += ' AND ct.id=' + client_id
        else:
            auth_user = Profile.objects.get(auth=request.user.id)
            tail += ' AND ct.id=' + str(auth_user.client_id)

        device_id = request.GET.get('device_id')

        if device_id and device_id.isdigit():
            tail += ' AND dt.id=' + device_id

        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                dt.id AS device_id,
                dt.name AS device_name,
                dt.address AS device_address,
                ct.id AS client_id,
                ct.name AS client_name,
                DATE_FORMAT(st.`timestamp`, "%d.%m.%Y %H:%i:%s") AS `timestamp`,
                uft.name AS family_name,
                ut.name AS unit_name,
                ut.title AS unit_title,
                ut.format,
                dct.id AS mounted_unit_id,
                st.state AS mounted_unit_state
            FROM {devices_table} AS dt
                INNER JOIN {clients_table} AS ct
                    ON ct.id = dt.client_id
                INNER JOIN {devices_config_table} AS dct
                    ON dct.device_id = dt.id
                INNER JOIN {units_table} AS ut
                    ON ut.id = dct.unit_id
                INNER JOIN {units_family_table} AS uft
                    ON uft.id = ut.family_id
                INNER JOIN status AS st
                    ON st.unit_id = dct.id
            WHERE (1)
                {tail}
            ORDER BY dt.id, ut.family_id;
        '''.format(
            devices_table=Device._meta.db_table,
            clients_table=Client._meta.db_table,
            devices_config_table=Config._meta.db_table,
            units_table=Unit._meta.db_table,
            units_family_table=Family._meta.db_table,
            tail=tail
        ))

        entries = utils.list_fetchall(cursor)
        devices = {}

        cursor.close()

        for entry in entries:
            device_id = entry['device_id']

            if not device_id in devices:
                devices[device_id] = {
                    'id': device_id,
                    'name': entry['device_name'],
                    'address': entry['device_address'],
                    'client_id': entry['client_id'],
                    'client_name': entry['client_name'],
                    'status': {},
                }

            family_name = entry['family_name']

            if not devices[device_id]['status'].get(family_name):
                devices[device_id]['status'][family_name] = {}

            try:
                format_ = json.loads(entry['format'])
            except (json.decoder.JSONDecodeError, TypeError):
                format_ = {}

            state = entry['mounted_unit_state']
            format_values = format_.get('values', {})
            format_values_subkey = format_values.get(
                state, format_values.get('else', {})
            )

            mounted_unit_format = {
                'title': format_.get(
                    'title', entry['unit_title'],
                ),
                'chart': format_.get('chart'),
                'control': format_.get('control'),
                'values': list(
                    filter(
                        lambda x: x != 'else',
                        format_values.keys(),
                    )
                )
            }

            format_type = format_.get('type', '')

            if format_type == 'FLOAT_RANGE':
                state_float = utils.to_float(state)
                mounted_unit_format['state'] = state_float
                mounted_unit_format['caption'] = format_ \
                    .get('format', '{0:.2f}') \
                    .format(utils.to_float(state)) \
                    .replace('.', ',')
                mounted_unit_format['class'] = format_values.get(
                    'else', {}).get('class')

                for key in format_values.pop('else', ''):
                    range_tuple = utils.str_range_to_tuple(key)

                    if range_tuple[0] <= state_float < range_tuple[1]:
                        mounted_unit_format['class'] = format_values[key] \
                            .get('class')

                        break

            else:
                if format_type == 'STRING':
                    mounted_unit_format['state'] = state
                elif format_type == 'INTEGER':
                    mounted_unit_format['state'] = utils.to_int(state)

                mounted_unit_format['caption'] = format_values_subkey.get(
                    'title', state,
                )
                mounted_unit_format['class'] = format_values_subkey.get(
                    'class', 'bg-light bd bdc-brown-100 text-dark',
                )

            devices[device_id]['status'][family_name][entry['unit_name']] = {
                'id': entry['mounted_unit_id'],
                'name': entry['unit_name'],
                'title': entry['unit_title'],
                'format': mounted_unit_format,
                'timestamp': entry['timestamp'],
                'state': entry['mounted_unit_state'],
            }

        return devices
