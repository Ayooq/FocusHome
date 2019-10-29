from django.http import JsonResponse
import Django.util as util
from Devices.models import Device
from django.db import connection, transaction
from Monitoring.dispatcher import dispatcher


def index(request):
    if not request.profile.has_perm('app.devices.index'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    device_client = request.GET.get('client', None)
    device_name = request.GET.get('name', None)
    device_address = request.GET.get('address', None)

    cursor = connection.cursor()
    query = """
        SELECT
              d.id as device_id
            , d.name as device_name
            , d.address as device_address
            , d.comment as device_comment
            , c.id as client_id
            , c.name as client_name
        FROM devices as d
            inner join clients as c
                on c.id = d.client_id
        where d.id > 0
            """ + (" and c.name like %(device_client)s" if device_client else '') + """
            """ + (" and d.name like %(device_name)s" if device_name else '') + """
            """ + (" and d.address like %(device_address)s" if device_address else '') + """
            """ + (" and d.client_id = %(client_id)s" if request.user.role_code == 'clients' else '') + """
    """
    cursor.execute(query, {
        "device_client": '%' + device_client + '%',
        "device_name": '%' + device_name + '%',
        "device_address": '%' + device_address + '%',
        "client_id": request.user.client_id
    })

    devices = util.dictfetchall(cursor)

    return JsonResponse({
        "title": 'Оборудование',
        "data": devices,
    }, status=200)


def edit(request):
    if not request.profile.has_perm('app.devices.show'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    device_id = request.GET.get('device_id', 0)

    device = Device(device_id)

    return JsonResponse({
        "title": 'Оборудование. ' + device.device_name,
        "device": device.to_dict(),
        'units': device.get_units(gpio_format='json'),
        'pins': device.get_pins(),
        'gpio_types': device.get_monitoring_gpio_types(),
        'chart_types': device.get_monitoring_chart_types(),
        'gpio_controls': device.get_monitoring_controls(),
        'gpio_widget_formats': device.get_monitoring_widget_formats(),
        'is_client_change': request.profile.has_perm('app.devices.client.change'),
        'is_snmp_change': request.profile.has_perm('app.devices.snmp'),
    }, status=200)


def update(request):
    if not request.profile.has_perm('app.devices.update'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    if request.method == 'POST':
        body = request.body
        post = util.toJson(body)

        device_id = post.get('device_id', 0)
        units = post.get('units', None)

        device = Device()

        transaction.set_autocommit(False)
        cursor = connection.cursor()

        for item in units:
            gpio__format = item.get('gpio__format')
            validate = device.unitValidate(gpio__format, item.get('family__title','')+'/'+item.get('units__title',''))
            if validate == 1:
                query = """
                    INSERT INTO devices_config (
                        `pin`, `format`,
                        `device_id`, `unit_id`,
                        `src_id`
                    ) VALUES (
                        %(gpio_pin)s, %(gpio_format)s,
                        %(device_id)s, %(unit_id)s,
                        %(src_id)s
                    )
                    ON DUPLICATE KEY UPDATE
                        `pin`    = VALUES (`pin`),
                        `format` = VALUES (`format`),
                        `src_id` = VALUES (`src_id`)
                """

                src_id = None
                src_id_post = item.get('src_id', "")
                if type(src_id_post) == str:
                    if src_id_post.isdigit():
                        src_id = int(src_id_post)
                if type(src_id_post) == int:
                    src_id = src_id_post

                cursor.execute(query, {
                    'device_id': device_id,
                    'unit_id': item.get('units__id', 0),
                    'src_id': src_id,
                    'gpio_pin': item.get('gpio__pin', 0),
                    'gpio_format': util.jsonToStr(gpio__format) if not bool(gpio__format.get('is_default',True)) else None
                })
            else:
                transaction.rollback()
                cursor.close()
                return JsonResponse({
                    'message': validate
                }, status=400)

        device_data = post.get('device', None)
        if type(device_data) != dict:
            transaction.rollback()
            cursor.close()
            return JsonResponse({
                'message': 'неверный формат данных'
            }, status=400)

        device_address = str(device_data.get('device_address', '')).strip()
        device_comment = str(device_data.get('device_comment', '')).strip()

        query = """
            UPDATE devices
            SET address=%(device_address)s, comment=%(device_comment)s,
            snmp_host=%(snmp_host)s, snmp_community=%(snmp_community)s, snmp_version=%(snmp_version)s,
            snmp_user=%(snmp_user)s, snmp_password=%(snmp_password)s
            WHERE id=%(device_id)s;
        """
        cursor.execute(query, {
            'device_id': device_id,
            'device_address': device_address,
            'device_comment': device_comment,
            'snmp_host': str(device_data.get('snmp_host', '')).strip(),
            'snmp_community': str(device_data.get('snmp_community', '')).strip(),
            'snmp_version': str(device_data.get('snmp_version', '')).strip(),
            'snmp_user': str(device_data.get('snmp_user', '')).strip(),
            'snmp_password': str(device_data.get('snmp_password', '')).strip(),
        })

        transaction.commit()
        cursor.close()

        return JsonResponse({
            'message': 'update'
        }, status=200)

    return JsonResponse({
        'message': 'метод не найден'
    }, status=404)


def create(request):
    if not request.profile.has_perm('app.devices.create'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    if request.method == 'GET':
        return __create_get(request)
    if request.method == 'POST':
        return __create_post(request)

    return JsonResponse({
        'message': 'метод не найден'
    }, status=404)


def __create_get(request):
    device = Device()

    return JsonResponse({
        "title": 'Оборудование. Добавить новое',
        "device": device.get(),
        'units': device.get_units(gpio_format='json'),
        'pins': device.get_pins(),
        'gpio_types': device.get_monitoring_gpio_types(),
        'chart_types': device.get_monitoring_chart_types(),
        'gpio_controls': device.get_monitoring_controls(),
        'gpio_widget_formats': device.get_monitoring_widget_formats(),
        'is_client_change': False,
        'is_snmp_change': False,
    }, status=200)


def __create_post(request):
    body = request.body
    post = util.toJson(body)

    device_id = 0
    units = post.get('units', None)
    client_id = 0 #post.get('client_id', 0)

    device = Device()

    transaction.set_autocommit(False)
    cursor = connection.cursor()

    device_data = post.get('device', None)
    if type(device_data) != dict:
        transaction.rollback()
        cursor.close()
        return JsonResponse({
            'message': 'неверный формат данных'
        }, status=400)

    device_address = str(device_data.get('device_address', '')).strip()
    device_comment = str(device_data.get('device_comment', '')).strip()

    if client_id == 0:
        client_id = request.user.client_id

    for item in units:
        gpio__format = item.get('gpio__format')
        validate = device.unitValidate(gpio__format, item.get('family__title', '') + '/' + item.get('units__title', ''))
        if validate != 1:
            transaction.rollback()
            cursor.close()
            return JsonResponse({
                'message': validate
            }, status=400)

    query = """
        INSERT INTO devices
        (address, comment, client_id,
        snmp_host,snmp_community,snmp_version,
        snmp_user,snmp_password)
        VALUES(%(device_address)s, %(device_comment)s, %(client_id)s, 
        %(snmp_host)s, %(snmp_community)s, %(snmp_version)s,
        %(snmp_user)s, %(snmp_password)s
        );
    """
    cursor.execute(query, {
        'device_address': device_address,
        'device_comment': device_comment,
        'client_id': client_id,
        'snmp_host': str(device_data.get('snmp_host', '')).strip(),
        'snmp_community': str(device_data.get('snmp_community', '')).strip(),
        'snmp_version': str(device_data.get('snmp_version', '')).strip(),
        'snmp_user': str(device_data.get('snmp_user', '')).strip(),
        'snmp_password': str(device_data.get('snmp_password', '')).strip(),
    })

    query = """
        SELECT last_insert_id()
    """
    cursor.execute(query)
    row = cursor.fetchone()
    device_id = row[0]

    for item in units:
        gpio__format = item.get('gpio__format')
        query = """
            INSERT INTO devices_config (
                `pin`, `format`,
                `device_id`, `unit_id`,
                `src_id`
            ) VALUES (
                %(gpio_pin)s, %(gpio_format)s,
                %(device_id)s, %(unit_id)s,
                %(src_id)s
            )
            ON DUPLICATE KEY UPDATE
                `pin`    = VALUES (`pin`),
                `format` = VALUES (`format`),
                `src_id` = VALUES (`src_id`)
        """
        cursor.execute(query, {
            'device_id': device_id,
            'unit_id': item.get('units__id', 0),
            'src_id': item.get('src_id', None) if util.toInt(item.get('src_id', 0)) > 0 else None,
            'gpio_pin': item.get('gpio__pin', 0),
            'gpio_format': util.jsonToStr(gpio__format) if not bool(gpio__format.get('is_default', True)) else None
        })

    transaction.commit()
    cursor.close()

    return JsonResponse({
        'message': 'create',
        'device_id': device_id
    }, status=200)


def reboot(request, *args):
    if not request.profile.has_perm('app.devices.reboot'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    if request.method == 'POST':
        body = request.body
        post = util.toJson(body)
        device_id = post.get('device_id', None)

        dispatcher.device_reboot(
            device_id=device_id,
            user_id=request.user.id
        )

        return JsonResponse({
            'message': 'Команда перезагрузки отправлена на удаленное устройство',
            'device_id': device_id
        }, status=200)

    return JsonResponse({
        'message': 'Метод не определен'
    }, status=404)


def client_change(request, *args):
    if not request.profile.has_perm('app.devices.client.change'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    body = request.body
    post = util.toJson(body)

    device_id = post.get('device_id', 0)
    new_client_id = post.get('client_id', 0)

    cursor = connection.cursor()

    query = """
        SELECT
            c.id
        FROM clients as c
        where c.id =%(client_id)s
    """
    cursor.execute(query, {
        "client_id": new_client_id
    })
    if cursor.rowcount == 0:
        return JsonResponse({
            'message': 'Указанный клиент не найден',
            'client_id': new_client_id
        }, status=400)

    query = """
        UPDATE devices
        SET client_id=%(new_client_id)s
        WHERE id=%(device_id)s
    """
    cursor.execute(query, {
        'device_id': device_id,
        'new_client_id': new_client_id
    })

    return JsonResponse({
        'message': 'update',
        'client_id': new_client_id
    }, status=200)
