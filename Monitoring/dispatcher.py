import Monitoring.libs.focusSNMP.server as focus_snmp_server
import Django.util as util
import requests
from django.db import connection
from Devices.models import Device
import json
import os

# >>> r = requests.post("http://bugs.python.org", data={'number': 12524, 'type': 'issue', 'action': 'show'})
# >>> print(r.status_code, r.reason)
# 200 OK
# >>> print(r.text[:300] + '...')

class Dispatcher:
    DISPATCHER_SERVER_URL = "http://127.0.0.1:3000/"
    MONITORING_KEY = "x9oBNohwtf2p81jOZ5GuKweWn1AI0XfwGDw1OhX0EPgcoTs0TW"

    def __init__(self):
        self.curl = requests.Session()
        self.cursor = connection.cursor()
        # self.curl.headers.update({'monitoring-key': self.MONITORING_KEY})

    # отправка сообщения на Брокер
    def send_to_broker(self, urlAction, device_id, topic, payload, payloadType='json', user_id=None):
        db_payload = payload
        if payloadType == 'json':
            db_payload = json.dumps(payload, indent=4, ensure_ascii=False)
            payload = util.jsonToStr(payload)
        if payloadType == 'str':
            payload = db_payload = str(payload)

        result_code = 0
        result_message = None

        device = Device(device_id)
        if device.device_id == 0:
            result_message = "Не удалось опредлить ID устройства"
            result_code = 0

        topic = device.device_name + topic

        if not result_message:
            try:
                r = self.curl.post(
                    self.DISPATCHER_SERVER_URL + urlAction,
                    data={
                        'topic': topic,
                        'monitoring_key': self.MONITORING_KEY,
                        'payload': payload
                    },
                    timeout=5)

                if int(r.status_code) == 200:
                    result_code = 1
                else:
                    result_message = r.text
                    result_code = 0
            except Exception as ex:
                result_message = ex
                result_code = 0

        self.cursor.callproc('broker_dispatcher_log_add', (
            user_id,
            device.device_id,
            topic,
            db_payload,
            'django dispatcher',
            result_code,
            result_message
        ))

        return result_code


    #SNMP
    # добавить адрес для отслеживания/изменить интервал
    def monitoring_snmp_addr_add(self, **kwargs):
        addr = kwargs.get('addr', '')
        interval = kwargs.get('interval', 60*24)

        payload = {
            'OID': addr,
            'interval': interval
        }

        return self.send_to_broker(
            urlAction='send_message_to_device',
            device_id=kwargs.get('device_id', 0),
            topic="/snmp/watch/add",
            payload=payload,
            user_id=kwargs.get('user_id')
        )


    # удалить адрес из отслеживаний
    def monitoring_snmp_addr_remove(self, **kwargs):
        addr = kwargs.get('addr', '')

        payload = {
            'OID': addr
        }

        return self.send_to_broker(
            urlAction='send_message_to_device',
            device_id=kwargs.get('device_id', 0),
            topic="/snmp/watch/remove",
            payload=payload,
            user_id=kwargs.get('user_id')
        )


    # запрос на обновление значения
    def monitoring_snmp_reload_value(self, **kwargs):
        payload = {
            'OID': kwargs.get('addr', '')
        }

        return self.send_to_broker(
            urlAction='send_message_to_device',
            device_id=kwargs.get('device_id', 0),
            topic="/snmp/oid/get",
            payload=payload,
            user_id=kwargs.get('user_id')
        )


    # мониторинг показателя
    def snmp_sensor_set_notification(self, device_id, addr, notifications, **kwargs):
        # notifications - list ['условие значение','']
        # возможно, малинке об этом не стоит знать
        pass


    # отправка запроса на малинку для обновления всех показаний
    def snmp_get_image(self, **kwargs):
        # payload = {
        #     'OID': kwargs.get('addr', '')
        # }

        result_code = self.send_to_broker(
            urlAction='send_message_to_device',
            device_id=kwargs.get('device_id', 0),
            topic="/snmp/get",
            payload='',
            user_id=kwargs.get('user_id')
        )

        status = 'Запрос успешно отправлен'
        if result_code == 0:
            status = "Произошла ошибка"

        return status


    # загрузка отслеживаемых датчиков
    def snmp_set_value(self, **kwargs):
        snmp = focus_snmp_server.SNMP(connector=util.MSSQLConnector)
        filePath = kwargs.get('filePath', '')
        if os.path.isfile(filePath):
            # если писать в историю и проверять уведомления
            result = snmp.insert_history(filePath, kwargs.get('device_id', 0))
            # если просто обновить значение
            result = snmp.insert_value(filePath, kwargs.get('device_id', 0))
        else:
            return 0

        # данные, которые были возвращены как уведомление
        for row in result:
            pass
            # device_id, addr, date_now, message, history_id, link_type, n_condition, n_value, type
            # device_id = row[0]

        return 1

    # загрузка снимка устройства
    def set_device_image(self, **kwargs):
        snmp = focus_snmp_server.SNMP(connector=util.MSSQLConnector)
        filePath = kwargs.get('filePath','')
        if os.path.isfile(filePath):
            snmp.load_file(filePath, kwargs.get('device_id', 0))
            return 1
        else:
            return 0

    # device
    def device_unit_toogle(self, **kwargs):
        next_state = kwargs.get('next_state', None)
        if next_state:
            return self.send_to_broker(
                urlAction='send_message_to_device',
                device_id=kwargs.get('device_id', 0),
                topic="/cmd/" + kwargs.get('unit_name', ''),
                payload=kwargs.get('next_state'),
                payloadType='str',
                user_id=kwargs.get('user_id')
            )

    # перезагрузка устройства
    def device_reboot(self, **kwargs):
        device = Device(kwargs.get('device_id', 0))

        if device.device_id == 0:
            return 0

        config = {
            "units": [],
            "snmp": {
                'host': device.snmp_host,
                'community': device.snmp_community,
                'version': device.snmp_version,
                'user': device.snmp_user,
                'password': device.snmp_password,
            },
            "device": {
                "name": device.device_name,
                "address": device.device_address
            }
        }

        for unit in device.get_units():
            config['units'].append([
                unit['family__name'],
                unit['units__name'],
                unit['gpio__pin']
            ])

        return self.send_to_broker(
            urlAction='send_message_to_device',
            device_id=kwargs.get('device_id', 0),
            topic="/cnf/self",
            payload=config,
            user_id=kwargs.get('user_id')
        )

    # routines
    # субпрограмма обновлена
    def routine_update(self, **kwargs):
        return self.send_to_broker(
            urlAction='send_message_to_device',
            device_id=kwargs.get('device_id', 0),
            topic="/cmd/routine/update",
            payload=kwargs,
            user_id=kwargs.get('user_id')
        )

    # субпрограмма создана
    def routine_insert(self, **kwargs):
        return self.send_to_broker(
            urlAction='send_message_to_device',
            device_id=kwargs.get('device_id', 0),
            topic="/cmd/routine/create",
            payload=kwargs,
            user_id=kwargs.get('user_id')
        )

    # субпрограмма удалена
    def routine_remove(self, **kwargs):
        return self.send_to_broker(
            urlAction='send_message_to_device',
            device_id=kwargs.get('device_id', 0),
            topic="/cmd/routine/remove",
            payload=kwargs,
            user_id=kwargs.get('user_id')
        )


dispatcher = Dispatcher()
