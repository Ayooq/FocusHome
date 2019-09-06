import Django.util as util
from django.http import JsonResponse
from Devices.models import Device
from Monitoring.models import Monitoring
from django.db import connection
import json
from Monitoring.dispatcher import dispatcher
import Monitoring.libs.focusSNMP.server as focus_snmp_server


PAGE_TITLE = "Мониторинг"

# отметить уведомление как прочитанное
# пользователь, запросивший действие, должен иметь право на просмотр данного уведомления
def notification_set_read(user_id, nid):
    cursor = connection.cursor()
    query = """
        SELECT 
            sa.id
        from profiles as p
            inner join devices as d
                on d.client_id = p.client_id
            inner join snmp_alert as sa
                on sa.device_id = d.id
        where p.auth_id=%s and sa.id=%s
    """
    cursor.execute(query, (user_id, nid))

    if cursor.rowcount > 0:
        query = """
            UPDATE snmp_alert
            SET is_read=1, user_read=%s
            WHERE id=%s
        """
        cursor.execute(query, (user_id, nid))

        return 1

    cursor.close()
    return 0

# слияние массива объектов
# arr1 - исходный массив
# arr2 - массив шаблон
# fieldKey - свойство объекта по которому сравниваем
# fieldValue - свойство объекта, значение которого берем
def array_dicts_merge(arr1, arr2, fieldKey, fieldValue):
    arr = []

    for i2, item2 in enumerate(arr2):
        item = None
        for i1, item1 in enumerate(arr1):
            if arr1[i1][fieldKey] == arr2[i2][fieldKey]:
                item = {
                    fieldKey: arr1[i1][fieldKey],
                    fieldValue: arr1[i1][fieldValue]
                }
                break

        if item is None:
            item = {
                fieldKey: arr2[i2][fieldKey],
                fieldValue: arr2[i2][fieldValue]
            }

        arr.append(item)

    return arr


def api(request):
    if not request.profile.has_perm('app.monitoring.devices'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    action = request.GET.get('action', None)

    # device
    if action == 'devices_list':
        return devices_list(request)
    if action == 'device_info':
        return device_info(request)
    # if action == 'get_settings':
    #     return JsonResponse(Settings.all(request, group_id=1), status=200)
    if action == 'chart':
        return chart_data(request)
    if action == 'unit_toggle':
        return unit_toggle(request)

    # snmp
    if action == 'get_snmp':
        return get_snmp(request)
    if action == 'get_snmp_table':
        return get_snmp_table(request)
    if action == 'snmp_sensor_set_monitoring_interval':
        return snmp_sensor_set_monitoring_interval(request)
    if action == 'snmp_sensor_get_history':
        return snmp_sensor_get_history(request)
    if action == 'snmp_sensor_reload_value':
        return snmp_sensor_reload_value(request)
    if action == 'snmp_sensor_set_notification':
        return snmp_sensor_set_notification(request)
    if action == 'snmp_get_image':
        return snmp_get_image(request)
    if action == 'get_widgets':
        return get_widgets(request)
    if action == 'widget_add':
        return widget_add(request)
    if action == 'widget_remove':
        return widget_remove(request)

    # notifications
    if action == 'get_alerts':
        return get_alerts(request)
    if action == 'set_notification_read':
        return set_notification_read(request)

    # routines
    if action == 'get_routines':
        return get_routines(request)
    if action == 'routine_save':
        return routine_save(request)
    if action == 'routine_remove':
        return routine_remove(request)

    return JsonResponse({
        'message': 'Метод не определен'
    }, status=400)


def devices_list(request):
    devices = Monitoring.get_devices_list(request)

    return JsonResponse({
        'title': PAGE_TITLE,
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
        'title': PAGE_TITLE+'. ' + device.get('name', 'Ничего не найдено'),
        'data': device,
    }, status=200)


def chart_data(request):
    chartType = request.GET.get('chartType', None)
    device_id = request.GET.get('device_id', "")
    unit_id = request.GET.get('unitID', "")
    data = []
    unit = {'title': unit_id}

    if chartType in ('spline', 'area'):

        cursor = connection.cursor()
        query = """
            select
                dt.id as id,
                dt.name as name,
                dt.address as address,
                dt.name as uid,
                UNIX_TIMESTAMP(de.`timestamp`)*1000 as event__date,
                duf.title as event__family,
                duu.title as event__unit,
                de.message as event_message
            from devices as dt
                inner join clients as ct
                    on ct.id = dt.client_id
                left join events as de
                    on de.unit_id = %(unit_id)s
                left join devices_config as dug
                    on dug.id = de.unit_id
                left join units as duu
                    on duu.id = dug.unit_id
                left join units_family as duf
                    on duf.id = duu.family_id   
            where dt.id=%(device_id)s and de.`timestamp` > DATE_SUB(now(),Interval 1 MONTH)
            order by de.`timestamp` asc
        """
        cursor.execute(query, {'device_id': device_id, 'unit_id': unit_id})

        events_list = util.dictfetchall(cursor)
        events_list = events_list if events_list is not None else []

        if len(events_list) > 0:
            query = """
                select
                    COALESCE(dug.format, duu.format, "{{}}") as state_format
                from units as duu
                    left join devices_config as dug
                        on dug.id = '{unit_id}'
                limit 1
            """
            cursor.execute(query, {'unit_id': unit_id})
            units = util.dictfetchone(cursor)

            if units:
                state_format = json.loads(units['state_format']) if util.is_json(units['state_format']) else {}
                unit['title'] = state_format.get("title", unit_id)
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
    unit_id = request.GET.get('unitID', "")
    device_id = request.GET.get('device_id', 0)

    cursor = connection.cursor()
    query = """
        select
            de.state as state
        from devices as dt
            inner join clients as ct
                on ct.id = dt.client_id
            left join status as de
                on de.unit_id = %(unit_id)s    
        where dt.id=%(device_id)s and de.`timestamp` > DATE_SUB(now(),Interval 1 MONTH) #AND now()            
    """
    cursor.execute(query, {'device_id': device_id, 'unit_id': unit_id})
    events_list = util.dictfetchone(cursor)

    unit_state_current = events_list['state'] if events_list else 0
    unit_state_next = None

    query = """
        select
            COALESCE(dug.format, duu.format, "{{}}") as state_format,
            duu.name as unit_name
        from devices_config as dug
            left join units as duu
                on duu.id = dug.unit_id
        where dug.id = %(unit_id)s
    """
    cursor.execute(query, {'unit_id': unit_id})
    units = util.dictfetchone(cursor)
    cursor.close()

    if units:
        state_format = json.loads(units['state_format']) if util.is_json(units['state_format']) else {}
        state_format_values = state_format.get("values", [])
        unit_state_values = list(filter(lambda x: x['value'] != 'иначе', state_format_values))

        if len(unit_state_values) > 0:
            if unit_state_current is None:
                unit_state_next = unit_state_values[0]['value']
            else:
                for index, item in enumerate(unit_state_values):
                    if str(item['value']) == str(unit_state_current):
                        unit_state_next = unit_state_values[index + 1]['value'] if len(unit_state_values) > index + 1 else unit_state_values[0]['value']
                        break

        # передать значение состояния для установки - unit_state_next
        dispatcher.device_unit_toogle(
            device_id=device_id,
            unit_id=unit_id,
            unit_name=units['unit_name'],
            prev_state=unit_state_current,
            next_state=unit_state_next,
            user_id=request.user.id
        )

    return JsonResponse({
        'msg': "",
    }, status=200)


def get_snmp(request):
    addr = request.GET.get('addr', None)

    device_id = request.GET.get('device_id', 0)
    is_full = util.toInt(request.GET.get('full', 0))

    device = Device(device_id)

    data = {}
    notifications = {'conditions': []}
    cursor = connection.cursor()

    if addr:
        data = []

        if is_full == 0:
            data = []

            query = """
            select
                t.addr,
                t.value_type,
                COALESCE(t.mib_value, t.value) as value,
                t.mib_node_desc,
                case when sm.interval is null then 0 else sm.interval end as `interval`
            from snmp_device as t
                left join snmp_monitoring as sm
                    on sm.device_id = t.device_id
                    and sm.addr = t.addr
            where t.device_id = %s and t.addr like %s
            """
            cursor.execute(query, (device_id, addr + '%'))
            rows = cursor.fetchall()
            for row in rows:
                data.append({
                    'addr': row[0],
                    'value_type': row[1],
                    'value': row[2],
                    'desc': row[3],
                    'interval': row[4]
                })

        if is_full == 1:
            data = {}

            query = """
            select
                t.addr,
                t.value_type,
                t.value,
                DATE_FORMAT(t.updated, "%%d.%%m.%%Y %%H:%%i:%%s") as updated,
                t.mib_name,
                t.mib_syntax,
                t.mib_value,
                t.mib_node_name,
                t.mib_node_desc,
                case when sm.interval is null then 0 else sm.interval end as `interval`
            from snmp_device as t
                left join snmp_monitoring as sm
                    on sm.device_id = t.device_id
                    and sm.addr = t.addr
            where t.device_id = %s and t.addr = %s
            """
            cursor.execute(query, (device.device_id, addr))

            rows = util.dictfetchone(cursor)
            data = rows if rows else {}

            if 'addr' in data:
                query = """
                select
                      device_id
                    , addr
                    , `condition`
                    , `value`
                from snmp_notifications
                where device_id = %s and addr = %s
                """
                cursor.execute(query, (device.device_id, addr))
                rows = cursor.fetchall()
                for row in rows:
                    notifications['conditions'].append([row[2], row[3]])

    else:

        snmp = focus_snmp_server.SNMP(connector=util.MSSQLConnector)
        data = snmp.get_tree(device.device_id)

    return JsonResponse({
        'title': PAGE_TITLE+'. ' + device.device_name,
        'data': data,
        'notifications': notifications
    }, status=200)


def get_snmp_table(request):
    addr = request.GET.get('addr', None)
    # проверить права доступа к оборудованию
    device_id = request.GET.get('device_id', 0)

    snmp = focus_snmp_server.SNMP(connector=util.MSSQLConnector)
    columns, data = snmp.get_table(device_id, addr)

    return JsonResponse({
        'title': 'Список оборудования',
        'data': {"columns": columns, 'data': data}
    }, status=200)


def snmp_sensor_set_monitoring_interval(request):
    addr = request.GET.get('addr', None)
    device_id = request.GET.get('device_id', 0)
    interval = util.toInt(request.GET.get('interval', 0))

    cursor = connection.cursor()
    if interval > 0:
        cursor.execute("""
            INSERT INTO snmp_monitoring
                (
                    device_id, addr, `interval`
                )
            VALUES
                (
                    %s, '%s', %s
                )
            ON DUPLICATE KEY UPDATE
                `interval` = VALUES(`interval`)
        """ % (device_id, addr, interval)
                       )
        dispatcher.monitoring_snmp_addr_add(
            device_id=device_id,
            addr=addr,
            interval=interval,
            user_id=request.user.id)
    else:
        cursor.execute("""
            DELETE FROM snmp_monitoring
            WHERE device_id=%s AND addr='%s';
            """ % (device_id, addr)
                       )
        dispatcher.monitoring_snmp_addr_remove(
            device_id=device_id,
            addr=addr,
            user_id=request.user.id
        )

    return JsonResponse({
        'data': {"interval": interval}
    }, status=200)


def snmp_sensor_get_history(request):
    addr = request.GET.get('addr', None)
    device_id = request.GET.get('device_id', 0)
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    device = Device(device_id)

    _from = "2019-01-01 00:00"
    if util.is_date(date_from, r"[\d]{4}-[\d]{2}-[\d]{2}\s[\d]{2}:[\d]{2}"):
        _from = date_from
    _to = "2099-01-01 00:00"
    if util.is_date(date_to  , r"[\d]{4}-[\d]{2}-[\d]{2}\s[\d]{2}:[\d]{2}"):
        _to   = date_to

    cursor = connection.cursor()
    query = """
        SELECT id, device_id, addr, value, DATE_FORMAT(updated, "%%d.%%m.%%Y %%H:%%i:%%s") as updated, mib_value
        FROM focus.snmp_history
        WHERE device_id=%s and addr=%s and updated BETWEEN %s AND %s
        order by updated
    """
    cursor.execute(query, (device.device_id, addr, _from, _to))

    rows = util.dictfetchall(cursor)
    data = rows if rows is not None else []

    return JsonResponse({
        'title': PAGE_TITLE+'. ' + device.device_name + '. История',
        'data': data
    }, status=200)


def snmp_sensor_reload_value(request):
    addr = request.GET.get('addr', None)
    device_id = request.GET.get('device_id', 0)

    new_value = dispatcher.monitoring_snmp_reload_value(
        device_id=device_id,
        addr=addr,
        user_id=request.user.id
    )

    return JsonResponse({
        'data': new_value
    }, status=200)


def snmp_sensor_set_notification(request):
    addr = request.GET.get('addr', None)
    device_id = request.GET.get('device_id', 0)
    notifications = request.GET.get('notifications', None)

    notif = {'conditions': []}
    if util.is_json(notifications):
        _notif = util.toJson(notifications)
        if 'conditions' in _notif:
            if type(_notif['conditions']) == list:
                for n in _notif['conditions']:
                    if len(n) == 2:
                        notif['conditions'].append(n)

    cursor = connection.cursor()
    query = """
        DELETE FROM snmp_notifications
        WHERE device_id=%s and addr=%s
    """
    cursor.execute(query, (device_id, addr))
    for c in notif['conditions']:
        query = """
            INSERT INTO snmp_notifications
            (device_id, addr, `condition`, value)
            VALUES(%s, %s, %s, %s);
        """
        cursor.execute(query, (device_id, addr, c[0], c[1]))

    dispatcher.snmp_sensor_set_notification(
        device_id=device_id,
        addr=addr,
        conditions=notif['conditions'],
        user_id=request.user.id
    )

    return JsonResponse({
        'notification': notif
    }, status=200)


def snmp_get_image(request):
    device_id = request.GET.get('device_id', 0)

    status = dispatcher.snmp_get_image(
        device_id=device_id,
        user_id=request.user.id
    )

    return JsonResponse({
        'status': status
    }, status=200)


def get_widgets(request):
    device_id = request.GET.get('device_id', 0)

    device = Device(device_id)

    cursor = connection.cursor()
    query = """
        SELECT 
              w.device_id
            , w.addr
            , w.title
            , w.comment
            , d.value_type
            , d.mib_value
            , d.value
            , DATE_FORMAT(d.updated, "%%d.%%m.%%Y %%H:%%i:%%s") as updated
            , d.mib_name
            , d.mib_node_name
            , d.mib_node_desc
            , m.interval
        FROM snmp_widgets as w
            inner join snmp_device as d
                on d.device_id = w.device_id
                and d.addr = w.addr
            left join snmp_monitoring as m
                on m.device_id = w.device_id
                and m.addr = w.addr
        WHERE w.device_id=%s;
    """
    cursor.execute(query, (device_id))

    rows = util.dictfetchall(cursor)

    return JsonResponse({
        'title': PAGE_TITLE + '. ' + device.device_name + '. Виджеты',
        'data': rows
    }, status=200)


def widget_add(request):
    body = request.body
    status = 0

    device = Device()

    if util.is_json(body):
        post = util.toJson(body)
        addr = post.get('addr', None)
        device_id = post.get('device_id', 0)
        widget = post.get('widget', {})

        device = Device(device_id)

        if type(widget) == dict:
            cursor = connection.cursor()
            query = """
                REPLACE INTO snmp_widgets
                    (
                        device_id, addr, title, comment
                    )
                VALUES(
                        %s, %s, %s, %s
                    )
            """
            cursor.execute(query, (device_id, addr, widget.get('title',''), widget.get('comment','')))
            status = 1


    return JsonResponse({
        'title': PAGE_TITLE + '. ' + device.device_name + '. Добавить виждет',
        'status': status
    }, status=200)


def widget_remove(request):
    body = request.body
    status = 0

    if util.is_json(body):
        post = util.toJson(body)
        addr = post.get('addr', '')
        device_id = post.get('device_id', 0)

        cursor = connection.cursor()
        query = """
            DELETE FROM snmp_widgets
            WHERE device_id=%s AND addr=%s;
        """
        cursor.execute(query, (device_id, addr))
        status = 1

    return JsonResponse({
        'status': status
    }, status=200)


def get_alerts(request):
    user_id = request.user.id
    is_read = util.toInt(request.GET.get('is_read', 0))
    limit = util.toInt(request.GET.get('limit', 5))
    full = util.toInt(request.GET.get('full', 0))
    device_id = util.toInt(request.GET.get('device_id', 0))
    device_oid = request.GET.get('device_oid', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    _from = "2019-01-01 00:00"
    if util.is_date(date_from, r"[\d]{4}-[\d]{2}-[\d]{2}\s[\d]{2}:[\d]{2}"):
        _from = date_from
    _to = "2099-01-01 00:00"
    if util.is_date(date_to, r"[\d]{4}-[\d]{2}-[\d]{2}\s[\d]{2}:[\d]{2}"):
        _to = date_to

    cursor = connection.cursor()

    query = """
        SELECT 
             d.name as device_name
            , sa.addr
            , DATE_FORMAT(sa.created, "%%d.%%m.%%Y %%H:%%i:%%s") as created
            , sa.device_id
            , sa.history_id
            , sa.id
            , sa.link_type
            , sa.message
            , sa.is_read
            , DATE_FORMAT(sa.updated, "%%d.%%m.%%Y %%H:%%i:%%s") as updated
            , sa.type
            , sa.n_condition
            , sa.n_value
            , sh.value as h_value
        from auth_user as au
            inner join devices as d
                on d.client_id = au.client_id
            inner join snmp_alert as sa
                on sa.device_id = d.id
            inner join snmp_history as sh
                on sh.id = sa.history_id
        where au.id=%(user_id)s
            and sa.updated between %(_from)s and %(_to)s
            """ + (('and sa.is_read=%(is_read)s' if is_read > -1 else '')) + """
            """ + (('and d.id=%(device_id)s' if device_id > 0 else '')) + """
            """ + (('and sa.addr like %(device_oid)s' if device_oid else '')) + """
        order by sa.updated desc
    """
    cursor.execute(query, {
        'user_id': user_id,
        '_from': _from,
        '_to': _to,
        'is_read': is_read,
        'device_id': device_id,
        'device_oid': '%'+device_oid+'%'
    })
    rowcount = cursor.rowcount

    result = util.dictfetchall(cursor)[:limit]

    conditions = {
        'lt' :'меньше',
        'gt' :'больше',
        'eq' :'равно',
        'like' :'содержит',
        'not_like' :'не содержит'
    }

    for index, item in enumerate(result):
        condition = "Значение ("+item['h_value']+") "+conditions.get(item['n_condition'], '')+" "+item['n_value']

        result[index]['condition'] = condition

    devices = []
    if full == 1:
        query = """
            SELECT 
                 d.id
                , d.name
            from profiles as p
                inner join devices as d
                    on d.client_id = p.client_id
            where p.auth_id=%s
            order by d.name
        """
        cursor.execute(query, (user_id, ))
        devices = cursor.fetchall()

    return JsonResponse({
        'data': result,
        'count': rowcount,
        'devices': devices
    }, status=200)


def set_notification_read(request):
    user_id = request.user.id
    nid = request.GET.get('nid', 0)

    notification_set_read(user_id, nid)

    return get_alerts(request)


def get_routine_by_id(device_id, id):

    id = util.toInt(id)

    cursor = connection.cursor()
    query = """
        SELECT 
            dr.id
            , dr.device_id
            , dr.name
            , dr.comment
            , dr.instruction
        FROM focus.device_routines as dr
        WHERE dr.id = %(id)s
    """
    cursor.execute(query, {"id": id})
    data = util.dictfetchone(cursor)

    if id > 0 and data is None:
        return JsonResponse({
            'message': 'Программа не найдена'
        }, status=404)

    if data:
        if util.is_json(data['instruction']):
            data['instruction'] = util.toJson(data['instruction'])
        else:
            data['instruction'] = {
                "routine": {
                    "conditions": [],
                    "actions": []
                }
            }
    else:
        data = {
            "device_id": util.toInt(device_id),
            "name": "",
            "comment": "",
            "instruction": {
                "routine": {
                    "conditions": [],
                    "actions": []
                }
            }
        }

    units = []
    query = """
        SELECT
              u.name as name
            , u.title as title
        from devices_config as dc
            inner join units as u
                on u.id = dc.unit_id
        where dc.device_id = %(device_id)s
    """
    cursor.execute(query, {"device_id": device_id})
    units = util.dictfetchall(cursor)

    functions = {}
    query = """
        SELECT
              drb.name
            , drb.params
            , drb.comment
        from device_routines_builtin as drb
        where drb.device_id in (-1, %(device_id)s)
        order by drb.name
    """
    cursor.execute(query, {"device_id": device_id})
    functions_list = util.dictfetchall(cursor)

    for index, item in enumerate(functions_list):
        if util.is_json(item['params']):
            functions_list[index]['params'] = util.toJson(item['params'])
        else:
            functions_list[index]['params'] = []
        functions[functions_list[index]['name']] = functions_list[index]

    compares = {
        "eq": {"name": "eq", "value": "равно", "desc": "="},
        "ne": {"name": "ne", "value": "не равно", "desc": "<>"},
        "lt": {"name": "lt", "value": "меньше", "desc": "<"},
        "gt": {"name": "gt", "value": "больше", "desc": ">"},
        "le": {"name": "le", "value": "меньше или равно", "desc": "<="},
        "ge": {"name": "ge", "value": "больше или равно", "desc": ">="}
    }

    modes = [
        {"name": "and", "value": "и"},
        {"name": "or", "value": "или"},
    ]

    actions = [
        {"name": "setValue", "value": "установить значение"},
        {"name": "call", "value": "вызвать функцию"},
    ]

    for i, a in enumerate(data['instruction']['routine']['actions']):
        if a['action'] == "call":
            if a['function'] in functions:
                data['instruction']['routine']['actions'][i]['params'] = array_dicts_merge(
                    a['params'],
                    functions[a['function']]['params'],
                    'name', 'value'
                )
            else:
                data['instruction']['routine']['actions'][i]['function'] = ""
                data['instruction']['routine']['actions'][i]['params'] = []

    return JsonResponse({
        'data': data,
        'units': units,
        'compares': compares,
        'functions': functions,
        'modes': modes,
        'actions': actions,
    }, status=200)


def get_routines(request):
    device_id = request.GET.get('device_id', 0)
    id = request.GET.get('id', None)
    r_name = request.GET.get('name', '')

    if id is not None:
        return get_routine_by_id(device_id, util.toInt(id))

    cursor = connection.cursor()
    query = """
        SELECT 
            dr.id
            , dr.device_id
            , dr.name
            , dr.comment
            #, dr.instruction
        FROM device_routines as dr
        WHERE dr.device_id=%(device_id)s
            """ + ('and dr.name like %(r_name)s' if r_name else '') + """
        order by dr.name
    """
    cursor.execute(query, {"device_id": device_id, "r_name": '%' + r_name + '%'})

    data = util.dictfetchall(cursor)

    device = Device(device_id)

    return JsonResponse({
        'title': PAGE_TITLE + '. ' + device.device_name + '. Программы',
        'data': data
    }, status=200)


def routine_save(request):
    body = request.body

    if util.is_json(body):
        post = util.toJson(body)

        device_id = post.get('device_id', 0)
        routine_id = post.get('id', 0)
        routine_name = post.get('name', '')
        routine_comment = post.get('comment', '')
        instruction = post.get('instruction', None)

        if routine_name == '':
            return JsonResponse({
                'message': 'Заполните поле название'
            }, status=400)

        if type(instruction) == dict:
            routine = instruction.get('routine')
            if routine:
                if type(routine.get('conditions')) != list:
                    routine['conditions'] = []
                if type(routine.get('actions')) != list:
                    routine['actions'] = []
            else:
                routine = {'conditions':[], 'action':[]}

            cursor = connection.cursor()
            if routine_id == 0:
                query = """
                    INSERT INTO device_routines
                    (device_id, name, comment, instruction)
                    VALUES(
                        %(device_id)s,
                        %(routine_name)s,
                        %(routine_comment)s,
                        %(instruction)s
                    );
                """
            else:
                query = """
                    UPDATE device_routines
                    SET name=%(routine_name)s, comment=%(routine_comment)s, instruction=%(instruction)s
                    WHERE id=%(routine_id)s and device_id=%(device_id)s;
                """
                dispatcher.routine_update(
                    device_id=device_id,
                    routine_id=routine_id,
                    routine_name=routine_name,
                    routine_comment=routine_comment,
                    instruction=instruction,
                    user_id=request.user.id
                )

            cursor.execute(query, {
                "device_id": device_id,
                "routine_id": routine_id,
                "routine_name": routine_name,
                "routine_comment": routine_comment,
                "instruction": util.jsonToStr(instruction)
            })

            if routine_id == 0:
                query = """
                    select LAST_INSERT_ID() as routine_id
                """
                cursor.execute(query)

                row = cursor.fetchone()
                if row:
                    routine_id = row[0]

                    dispatcher.routine_insert(
                        device_id=device_id,
                        routine_id=routine_id,
                        routine_name=routine_name,
                        routine_comment=routine_comment,
                        instruction=instruction,
                        user_id=request.user.id
                    )
                else:
                    return JsonResponse({
                        'message': 'Не удалось создать программу'
                    }, status=400)

            return get_routine_by_id(device_id, routine_id)

    return JsonResponse({
        'message': 'data not found'
    }, status=400)


def routine_remove(request):
    body = request.body

    if util.is_json(body):
        post = util.toJson(body)

        device_id = post.get('device_id', 0)
        routine_id = post.get('id', 0)

        cursor = connection.cursor()
        query = """
            DELETE FROM focus.device_routines
            WHERE id=%(routine_id)s and device_id=%(device_id)s;
        """
        cursor.execute(query, {"device_id": device_id, "routine_id": routine_id})

        dispatcher.routine_remove(
            device_id=device_id,
            routine_id=routine_id,
            user_id=request.user.id
        )

    return JsonResponse({
        'data': 'routine_remove'
    }, status=200)
