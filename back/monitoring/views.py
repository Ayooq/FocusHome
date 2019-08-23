import json
from datetime import datetime
from dateutil import relativedelta as delta

from configuration.models import Configuration
from devices.models import Device
from events.models import Event
from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import make_aware
from focus import utils
from focus.mqtt import client
from profiles.models import Profile
from status.models import Status

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

        status=200
    )


def device_info(request):
    device_id = request.GET.get('device_id', '0')
    devices = Monitor.get_devices_dict(request, device_id=device_id)

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

        status=200
    )


def chart(request):
    chart_type = request.GET.get('chart_type')
    unit_id = request.GET.get('unit_id', '')
    data = []
    unit = {'title': unit_id}

    if chart_type in ('spline', 'area'):
        month_interval = datetime.now() - delta.relativedelta(months=1)
        queryset = Event.objects \
            .filter(timestamp__gte=make_aware(month_interval), unit=unit_id) \
            .select_related('unit', 'unit__unit', 'unit__device',
                            'unit__unit__family') \
            .values('message', 'timestamp', 'unit__device__name',
                    'unit__unit__name', 'unit__unit__family__title',
                    'unit__unit__format', 'unit__format', 'unit__unit__title'
                    )[:1]

        if queryset.count():
            entry = queryset[0]

            try:
                format_ = entry['unit__format'] or entry['unit__unit__format']
                format_ = json.loads(format_)
            except json.decoder.JSONDecodeError:
                format_ = {}

            unit['name'] = entry['unit__unit__name']
            unit['title'] = format_.get('title', entry['unit__unit__title'])
            unit['device'] = entry['unit__device__name']

            msg = entry['message']

            try:
                utils.to_float(msg)
                data.append(
                    (
                        entry['timestamp'],
                        msg,
                    )
                )
            except ValueError:
                pass

    return JsonResponse(
        {
            'unit': unit,
            'data': data,
        },

        status=200
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

        status=200
    )
