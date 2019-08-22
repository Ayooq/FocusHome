import json

from clients.models import Client
from configuration.models import Configuration
from devices.models import Device
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import redirect, render
from focus import utils
from focus.mqtt import client
from profiles.models import Profile
from status.models import Status
from units.models import Family, Unit

from .models import Monitor


@permission_required('monitoring.view_monitor')
def index(request):
    auth_user = Profile.objects.get(auth=request.user.id)

    if request.user.is_superuser:
        devices = Device.objects.all().order_by('name')
    else:
        devices = Device.objects \
            .filter(client=auth_user.client_id) \
            .order_by('name')

    paginator = Paginator(devices, utils.ITEM_PER_PAGE)
    page = request.GET.get('page')
    devices = paginator.get_page(page)
    settings = Configuration.fetch_settings(
        code=('monitoring_update_interval', )
    )

    return render(
        request, 'monitoring/index.html',
        {
            'page': {
                'title': utils.get_app_name('Мониторинг')
            },
            'devices': devices,
            'settings': settings,
        }
    )


@permission_required('monitoring.change_monitor')
def api(request):
    action = request.GET.get('action')

    if action == 'devices':
        return devices(request)
    if action == 'device_info':
        return device_info(request)
    if action == 'get_settings':
        return JsonResponse(Configuration.fetch_settings(request), status=200)
    if action == 'chart':
        return chart(request)
    if action == 'unit_toggle':
        return unit_toggle(request)

    return JsonResponse({'data': []}, status=404)


def devices(request):
    devices = Monitor.get_devices_dict(request)

    return JsonResponse(
        {
            'title': 'Список оборудования',
            'data': devices,
            'num_pages': 0,
            'cur_index': int(request.GET.get('page', 1)),
            'start_index': 0,
            'end_index': 0,
            'client_choice': request.user.has_perm(
                'monitoring.change_monitor',
            ),
        },

        status=200,
    )


def device_info(request):
    device_id = request.GET.get('device_id', '0')
    devices = Monitor.get_devices_dict(request, device_id)

    data = devices.get(int(device_id), {})
    client = data.get('client_name')
    device = data.get('name')
    title = ' / '.join(
        [client, device]
    ) if client and device else 'Ничего не найдено'

    return JsonResponse(
        {
            'title': title,
            'data': data,
        },

        status=200,
    )


def chart(request):
    chart_type = request.GET.get('chart_type')
    unit_id = request.GET.get('unit_id', '')
    data = []
    unit = {'title': unit_id}

    if chart_type in ('spline', 'area'):
        tail = ''

        if not request.user.is_superuser:
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
                DATE_FORMAT(et.`timestamp`, "%d.%m.%Y %H:%i:%s") AS `timestamp`,
                uft.title AS family_title,
                ut.name AS unit_name,
                et.message AS message
            FROM {devices_table} AS dt
                INNER JOIN {clients_table} AS ct
                    ON ct.id = dt.client_id
                LEFT JOIN events AS et
                    ON et.unit_id = '{unit_id}'
                LEFT JOIN {devices_config_table} AS dct
                    ON dct.id = et.unit_id
                LEFT JOIN {units_table} AS ut
                    ON ut.id = dct.unit_id
                LEFT JOIN {units_family_table} AS uft
                    ON uft.id = ut.family_id
            WHERE et.`timestamp` > DATE_SUB(NOW(),INTERVAL 1 MONTH)
                {tail}
        '''.format(
            clients_table=Client._meta.db_table,
            devices_table=Device._meta.db_table,
            devices_config_table=Config._meta.db_table,
            tail=tail,
            unit_id=unit_id,
            units_table=Unit._meta.db_table,
            units_family_table=Family._meta.db_table,
        ))

        entries = utils.list_fetchall(cursor)

        if entries:
            cursor.execute('''
                SELECT
                    COALESCE(dct.format, ut.format, "{{}}") AS format
                FROM {units_table} AS ut
                    LEFT JOIN {devices_config_table} AS dct
                        ON dct.id = '{unit_id}'
                LIMIT 1
            '''.format(
                devices_config_table=Config._meta.db_table,
                unit_id=unit_id,
                units_table=Unit._meta.db_table,
            ))

            units = utils.list_fetchall(cursor)

            if units:
                try:
                    format_ = json.loads(units[0]['format'])
                except json.decoder.JSONDecodeError:
                    format_ = {}

                unit['name'] = entries[0]['unit_name']
                unit['title'] = format_.get('title', unit_id)
                unit['device'] = entries[0]['device_name']

        for e in entries:
            msg = e['message']

            try:
                utils.to_float(msg)
                data.append(
                    (
                        e['timestamp'],
                        msg,
                    )
                )
            except ValueError:
                pass

        cursor.close()

    return JsonResponse(
        {
            'unit': unit,
            'data': data,
        },

        status=200,
    )


def unit_toggle(request):
    unit_id = request.GET.get('unit_id', '')
    active_unit = Status.objects.get(unit=unit_id)
    format_ = active_unit.unit.format or active_unit.unit.unit.format

    try:
        format_ = json.loads(format_)
    except json.decoder.JSONDecodeError:
        format_ = {}

    values_available = format_.get('values', {})
    actual_values = list(
        filter(
            lambda x: x != 'else',
            values_available.keys()
        )
    )
    state = active_unit.state
    payload = None

    for index, value in enumerate(actual_values):
        if value == state:
            try:
                payload = actual_values[index + 1]
            except IndexError:
                payload = actual_values[0]

            topic = '{}/cmd/{}'.format(
                active_unit.unit.device.name,
                active_unit.unit.unit.name,
            )
            client.publish(topic, payload, qos=1)

            break

    return JsonResponse(
        {
            'msg': 'смотри {}::{} (device_id={}, unit_id={}, value={}=>{})'
            .format(
                __name__,
                'unit_toggle',
                active_unit.unit.device.id,
                unit_id,
                state,
                payload,
            ),
        },

        status=200,
    )
