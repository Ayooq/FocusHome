from django.core.paginator import Paginator
import Django.util as util
from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden, JsonResponse
from django.core import serializers
from Devices.models import Devices
from Profiles.models import Profiles
from Monitoring.models import Monitoring
from DeviceUnits.models import Family, GPIOConfig, Units
from Settings.models import Settings
from Clients.models import Clients
from django.db import connection
import json


def index(request):
    if not request.user.has_perm('Monitoring.mon_list'):
        return HttpResponseForbidden()

    user_auth = Profiles.objects.get(auth_id=request.user.id)
    if request.user.is_superuser == 1:
        devices = Devices.objects.all()
    else:
        devices = Devices.objects.filter(client_id=user_auth.client_id)

    paginator = Paginator(devices, util.ITEM_PER_PAGE)
    page = request.GET.get('page')
    devices_list = paginator.get_page(page)

    return render(
        request, 'monitoring/index.html',
        {
            'page': {
                'title': util.get_app_name('Мониторинг')
            },
            'devices': devices_list,
            'settings': Settings.get(code=('monitoring_update_period',))
        }
    )


def api(request):
    if not request.user.has_perm('Monitoring.mon_list'):
        return HttpResponseForbidden()

    action = request.GET.get('action', None)

    if action == 'devices_list':
        return devices_list(request)
    if action == 'device_info':
        return device_info(request)
    if action == 'get_settings':
        return JsonResponse(Settings.all(request, group_id=1), status=200)
    if action == 'chart':
        return chart_data(request)
    if action == 'unit_toggle':
        return unit_toggle(request)

    return JsonResponse({'data':[]}, status=404)


def devices_list(request):
    devices = Monitoring.get_devices_list(request)

    return JsonResponse({
        'title': 'Список оборудования',
        'data': devices,
        'num_pages': 0,
        'cur_index': int(request.GET.get('page', 1)),
        'start_index': 0,
        'end_index': 0,
        'client_change': request.user.has_perm('Monitoring.mon_list')
    }, status=200)


def device_info(request):

    device = {}
    devices = Monitoring.get_devices_list(request)
    keys = devices.keys()
    if len(keys) > 0:
        device = devices.get(list(keys)[0], {})

    return JsonResponse({
        'title': device.get('client__name', '') + ' / ' + device.get('name','Ничего не найдено'),
        'data': device,
    }, status=200)


def chart_data(request):
    chartType = request.GET.get('chartType', None)
    unitID = request.GET.get('unitID', "")
    data = []
    unit = {'title': unitID}

    if chartType in ('line', 'area'):
        where = ""
        if request.user.is_superuser != 1:
            user_auth = Profiles.objects.get(auth_id=request.user.id)
            where += " and ct.id=" + str(user_auth.client_id)

        device_id = request.GET.get('device_id', False)
        if device_id:
            if device_id.isdigit():
                where += " and dt.id=" + str(device_id)

        cursor = connection.cursor()
        cursor.execute("""
            select
                dt.id as id,
                dt.name as name,
                dt.address as address,
                dt.uid as uid,
                UNIX_TIMESTAMP(de.`timestamp`)*1000 as event__date,
                duf.title as event__family,
                duu.title as event__unit,
                de.message as event_message
            from {devices_table} as dt
                inner join {clients_table} as ct
                    on ct.id = dt.client_id
                left join events as de
                    on de.unit_id = '{unit_id}'
                left join {gpio_table} as dug
                    on dug.id = de.unit_id
                left join {units_table} as duu
                    on duu.id = dug.unit_id
                left join {family_table} as duf
                    on duf.id = duu.family_id   
            where de.`timestamp` > DATE_SUB(now(),Interval 1 MONTH) #AND now()
                {where}
            """.format(
                devices_table=Devices._meta.db_table,
                clients_table=Clients._meta.db_table,
                family_table=Family._meta.db_table,
                gpio_table=GPIOConfig._meta.db_table,
                units_table=Units._meta.db_table,
                unit_id=unitID,
                where=where
            )
        )
        events_list = util.dictfetchall(cursor)
        events_list = events_list if events_list is not None else []

        if len(events_list) > 0:
            cursor.execute("""
                select
                    COALESCE(dug.format, duu.format, "{{}}") as state_format
                from DeviceUnits_units as duu
                    left join DeviceUnits_gpioconfig as dug
                        on dug.id = '{unit_id}'
                limit 1
                """.format(
                    unit_id=unitID
                )
            )
            units = util.dictfetchall(cursor)
            units = units if units is not None else []

            if len(units) > 0:
                state_format = json.loads(units[0]['state_format']) if util.is_json(units[0]['state_format']) else {}
                unit['title'] = state_format.get("title", unitID)
                unit['device'] = events_list[0]['name']
                unit['name'] = events_list[0]['event__unit']

        for e in events_list:
            data.append((e['event__date'], util.toFloat(e['event_message'])))

        cursor.close()

    return JsonResponse({
        'unit': unit,
        'data': data,
    }, status=200)


def unit_toggle(request):
    unitID = request.GET.get('unitID', "")

    where = ""
    if request.user.is_superuser != 1:
        user_auth = Profiles.objects.get(auth_id=request.user.id)
        where += " and ct.id=" + str(user_auth.client_id)

    device_id = request.GET.get('device_id', False)
    if device_id:
        if device_id.isdigit():
            where += " and dt.id="+str(device_id)

    cursor = connection.cursor()
    cursor.execute("""
        select
            de.state as state
        from {devices_table} as dt
            inner join {clients_table} as ct
                on ct.id = dt.client_id
            left join status as de
                on de.unit_id = '{unit_id}'    
        where de.`timestamp` > DATE_SUB(now(),Interval 1 MONTH) #AND now()
            {where}
    """.format(
            devices_table=Devices._meta.db_table,
            clients_table=Clients._meta.db_table,
            unit_id=unitID,
            where=where
        )
    )
    events_list = util.dictfetchall(cursor)
    unit_state_values = []
    unit_state_current = None
    unit_state_next = None

    if len(events_list)>0:
        unit_state_current = events_list[0]['state']

    cursor.execute("""
        select
            COALESCE(dug.format, duu.format, "{{}}") as state_format
        from DeviceUnits_units as duu
            left join DeviceUnits_gpioconfig as dug
                on dug.id = '{unit_id}'
        limit 1
    """.format(
        unit_id=unitID
    )
    )
    units = util.dictfetchall(cursor)
    units = units if units is not None else []

    if len(units) > 0:
        state_format = json.loads(units[0]['state_format']) if util.is_json(units[0]['state_format']) else {}
        state_format_values = state_format.get("values", {})
        unit_state_values= list(filter(lambda x: x != 'else', list(state_format_values.keys())))

    cursor.close()

    if len(unit_state_values) > 0:
        if unit_state_current is None:
            unit_state_next = unit_state_values[0]
        else:
            for index, value in enumerate(unit_state_values):
                if str(value) == str(unit_state_current):
                    unit_state_next = unit_state_values[index+1] if len(unit_state_values) > index+1 else unit_state_values[0]
                    break

    # передать куда-то значение состояния для установки - unit_state_next
    # ...
    # ...


    return JsonResponse({
        'msg': "смотри {}::{} (DeviceID={}, unitID={}, value={}=>{})".format(__name__, "unit_toggle", device_id, unitID, unit_state_current, unit_state_next),
    }, status=200)
