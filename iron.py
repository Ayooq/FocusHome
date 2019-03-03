import logging
import yaml
import json

from threading import Thread
from time import sleep
#   # from threading import Timer

from gpiozero import CPUTemperature
from gpiozero import Button
from gpiozero import LED

from gpiozero import Device
from gpiozero.pins.mock import MockFactory

import paho.mqtt.client as mqtt

from report import Reporter
from logger import create_2_logger


class Worker(object):
    '''Базовый организатор обмена
    Запускает обмен как нитка. Устанавливает обработчик принятых сообщений
    '''
    def __init__(self, worker):
        # self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.receiver_thread = Thread(target=worker)
        self.receiver_thread.setDaemon(1)
        self.receiver_thread.start()

    def set_message_callback(self, callback):
        """Установить обработчик сообщения"""
        self.message_received = callback

    def message_received(self, message):
        """Обработчик сообщения по умолчанию"""
        raise NotImplementedError("Message callback not set")

    def quit(self):
        self.receiver_thread.join()


class GIron(object):
    '''Железо'''
    def __init__(self, device=None, **kwargs):
        self.description = kwargs.pop('description', None)
        self.pin = kwargs.pop('pin', None)
        self.ident = kwargs.pop('ident', None)
        if device:
            self.device = device(self.pin, **kwargs)    # железка по gpiozero
        else:
            self.device = None
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.reporter = Reporter(self.ident)
        self.logger.debug('Подготовка %s [%s]' % (self.ident, repr(self)))

    def registre(self, to, function):
        self.reporter.registre(to, function)

    def unregistre(self, to):
        self.reporter.unregistre(to)

    def __repr__(self):
        return "%s(%r, description=%r, pin=%r, id=%r)" % (
                self.__class__.__name__,
                self.device,
                self.description,
                self.pin,
                self.ident
                )


class GSwitch(GIron):
    '''Выключатель как LED'''
    def __init__(self, **kwargs):
        GIron.__init__(self, LED, **kwargs)
        #   self.logger = logging.getLogger('cfactory.%s' % __name__)
        #   self.reporter = Reporter(self.ident)
        self.logger.debug('Подготовка %s [%s]' % (self.ident, repr(self)))

    @property
    def state(self):
        return self.device.is_lit

    def on(self):
        '''Switch ON'''
        self.device.on()
        self.public(self.on.__doc__, 'ВКЛЮЧИЛ')

    def off(self):
        '''Switch OFF'''
        self.device.off()
        self.public(self.off.__doc__, 'ОТКЛЮЧИЛ')

    def toggle(self):
        '''Switch TOGGLE'''
        self.device.toggle()
        self.public(self.toggle.__doc__, 'ПЕРЕКЛЮЧИЛ')

    ''''
    def _is_bool(self, value):
        if isinstance(value, int):
            if val > 0:
                return True
            else:
                return False
        if isinstance(value, str):
            is val is ''
    '''

    def onoff(self, value):
        if value in ('ON', 'on', 1):
            self.on()
        else:
            self.off()

    def public(self, log_info, message):
        self.logger.debug(
            u'%s %s [%s]' %
            (self.description, message, repr(self))
            # (self.ident, message, repr(self))
        )
        self.logger.warning(
            u'%s %s' %
            (self.description, message)
            # (self.ident, message, repr(self))
        )
        self.reporter.event(self.description, message).public()


class LoadAverageCPU(object):
    '''Средняя загрузка ЦПУ'''

    def __init__(self, **kwargs):
        self.mini = kwargs.get('min', 0)
        self.mini = kwargs.get('max', 2)
        self.value = None

    def get_t(self):
        ''' TODO: Проверка на существование'''
        self.value = self.device(
                min_load_average=self.mini,
                max__load_average=self.maxi)


class GTemperature(CPUTemperature):
    '''Датчики температуры'''
    def __init__(self, **kwargs):
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.description = kwargs.pop('description', None)
        self.ident = kwargs.pop('ident', None)
        self.histeresis = kwargs.pop('histeresis', 0.0)
        # temp_file = kwargs.pop('sensor_file', None)
        CPUTemperature.__init__(self, **kwargs)
        self.wrk = Worker(self.more_then)
        self.reporter = Reporter(self.ident)
        self.logger.debug('Подготовка %s [%s]' % (self.ident, repr(self)))

    @property
    def temperature(self):
        if 'w1' in self.sensor_file:
            return self.w1_temperature()
        return self.cpu_temperature()

    def cpu_temperature(self):
        with open(self.sensor_file, 'r') as f:
            return float(f.readline().strip()) / 1000

    def w1_temperature(self):
        # with io.open(self.sensor_file, 'r') as f:
        with open(self.sensor_file, 'r') as f:
            return float(f.readlines()[1].split("=")[1]) / 1000

    def more_then(self):
        ''' Контроль за порогом'''
        self.more = None
        while(True):
            sleep(1)
            if self.is_active:
                if self.more:
                    continue
                self.public('Перегрев', self.temperature)
                self.more = True
            else:
                if self.more:
                    self.public('Норма', self.temperature)
                    self.more = False

    def registre(self, to, function):
        self.reporter.registre(to, function)

    def unregistre(self, to):
        self.reporter.unregistre(to)

    def public(self, log_info, message):
        self.logger.debug(
            u'%s %s(%s) [%s]' %
            (self.description, log_info, message, repr(self))
        )
        self.logger.warning(
            u'%s %s(%s)' %
            (self.description, log_info, message)
        )
        self.reporter.event(log_info, message).public()


class GControlSwitch(object):
    ''''''
    def __init__(self, **kwargs):
        self.ident = kwargs.pop('ident', None)
        kout = kwargs.pop('out', None)
        kcnt = kwargs.pop('cnt', None)
        self.switch = GSwitch(ident=self.ident + 'o', **kout)
        self.recept = GReceptor(True, ident=self.ident + 'c', **kcnt)
        self.sub = [self.switch, self.recept]
        self.value = False
        self.recept.addcallbacks(self.switchon, self.switchoff)

    def registre(self, grp, function):
        self.switch.registre(grp, function)
        self.recept.registre(grp, function)

    @property
    def state(self):
        return(self.switch.state, self.recept.state,)

    def on(self):
        self.switch.on()

    def off(self):
        self.switch.off()

    def onoff(self, value):
        self.switch.onoff(value)

    def switchon(self):
        '''Контроль ВКЛ'''
        if self.value:
            return
        if self.switch.device.is_lit:
            self.value = True
            self.recept.state = True
            self.recept.public(self.switchon.__doc__, 'ON')

    def switchoff(self):
        '''Контроль ВЫКЛ'''
        if self.switch.device.is_lit:
            return
        self.value = False
        self.recept.state = False
        self.recept.public(self.switchoff.__doc__, 'OFF')


class GReceptor(GIron):
    '''Концевой датчик'''
    def __init__(self, external_callback=False, **kwargs):
        GIron.__init__(self, Button, **kwargs)
        #   self.logger = logging.getLogger('cfactory.%s' % __name__)
        # self.enable_mock()
        self.gwait = False
        self.state = False
        self.interval = 2.0
        self.gwait = False
        if not external_callback:
            self.addcallbacks(self.on, self.off)
        # Через Reporter идет связка обмена данными
        #   self.reporter = Reporter(self.ident)
        self.logger.debug('Подготовка %s [%s]' % (self.ident, repr(self)))

    def addcallbacks(self, func1, func2):
        self.device.when_pressed = func1
        self.device.when_released = func2

    def enable_mock(self):
        '''Разрешение отладки'''
        self.state = False
        Device.pin_factory = MockFactory()
        self.btn_pin = Device.pin_factory.pin(self.pin)

    def test(self):
        if self.state:
            # Drive the pin low (this is what would happen electrically
            # when the button is pushed)
            self.btn_pin.drive_low()
            self.state = False
        else:
            self.btn_pin.drive_high()
            self.state = True

    def on(self):
        '''Кнопка нажата'''
        if self.state:
            return
        self.state = True
        if self.gwait:
            return
        self.public(self.on.__doc__, 'ON')

    def off(self):
        '''Кнопка отжата'''
        if self.device.is_pressed:
            self.state = True
            return
        self.state = False
        self.public(self.off.__doc__, 'OFF')

    def public(self, log_info, message):
        self.logger.debug(
            u'%s %s [%s]' %
            (self.description, log_info, repr(self))
            # (self.ident, log_info, repr(self))
        )
        self.logger.warning(
            u'%s %s' %
            (self.description, log_info)
            # (self.ident, log_info, repr(self))
        )
        self.reporter.event(self.description, message).public()


class Irons(object):
    '''Оборудование
    Разбито на именнованые группы
    '''
    def __init__(self, file_name='banka.yaml'):
        '''Настройка'''
        self.units = {}
        self.logger = create_2_logger(logging.DEBUG)
        #   logger.info('Banka start []')
        #   self.logger = logging.getLogger('cfactory.%s' % __name__)
        try:
            self.config = self.load_configure(file_name)
        except Exception as err:
            self.logger.debug(
                u'Ошибка! %s [%s] [%s]' %
                (self.__init__.__doc__, file_name, err)
            )
            raise
        self.reporter = Reporter(self.ident)
        self.wrk = Worker(self.iamlive)
        self.mk_units()
        self.logger.info('Старт %s' % self.ident)

    def mk_units(self):
        '''Создание справочника железа'''
        for key in self.config['units']:
            self.units[key] = self.set_units(self.config['units'][key])

    @property
    def inputs(self):
        '''Группа входы'''
        return self.units['input']

    @property
    def temp(self):
        '''датчики Температуры'''
        return self.units['ftemp']

    @property
    def complects(self):
        '''Комплекты '''
        return self.units['complect']

    @property
    def ident(self):
        return self.config['banka']['id']

    @property
    def delta(self):
        return self.config['banka']['time_report']

    def iamlive(self):
        '''Доклад'''
        pause = self.delta
        while(True):
            sleep(pause)
            self.reporter.event(
                'I am live',
                'Banka %s' % self.ident).public()
            # self.logger.info(
            #     'Banka %s %s' %
            #     (ident, 'I am live')
            # )

    def set_units(self, dictant):
        '''Установка '''
        dictant.pop('description', 'Нет описания')
        try:
            detal = eval(dictant.pop('dev', None))
            sub = {key: detal(ident=key, **dictant[key]) for key in dictant}
        except Exception:
            raise
        # sub['description'] = text
        return sub

    def load_configure(self, conf_file_name):
        """ Загрузка описателя оборудования из файла конфигурации.

        :param str conf_file_name: имя файла конфигурации для загрузки
        :rtype: `dict`

        .. warning::
            Конфигурационный файл должен быть доверительно проверен!
            Ссылки на имена классов позволяют выполнять произвольный код.
        """
        with open(conf_file_name, 'r') as f:
            conf_dict = yaml.load(f)
        return conf_dict

    def registre_all(self, function):
        ''' Регистрация внешнего viewera рапортов
            в поле to - имя группы железа
        '''
        for key, sub in self.units.items():
            for dev in sub:
                sub[dev].registre(key, function)

    def dumper(self, report):
        '''тестовый вывод'''
        print(u'Печатаю', json.dumps(report, ensure_ascii=False))

    def quit(self):
        self.logger.info('Стоп %s' % self.ident)


class Connector(Irons):
    '''Обвязка publisher mqtt вокруг Irons
    без учета авторизации !
    '''
    def __init__(self, config_file='banka.yaml', **kwargs):
        self.broker = kwargs.pop('broker', "192.168.1.252")
        Irons.__init__(self, config_file)
        self.client_id = kwargs.pop('id', str(self.ident))
        self.client = mqtt.Client(self.client_id)
        self.client.on_connect = self.on_connect
        self.client.connect(self.broker)
        self.registre_all(self.report2topic)

    def on_connect(self, client, userdata, rc, *extra_params):
        print('Connected with result code ' + str(rc))

    def report2topic(self, report):
        '''Форматирование сообщения на посредника'''
        topic = '%s/%s/%s/%s' % (
            str(self.ident),
            report['to'],
            report['from'],
            report['report']['types']
        )
        payload = report['report']['body']
        self.client.publish(topic, payload)
        #   self.logger.info('%s %s' % (topic, payload))

    def _del_(self):
        self.client.close()
        self.quit()


if __name__ == '__main__':
    from signal import pause

    irn = Connector('banka.yaml')

    #   client.connect(broker_address)  # connect to broker
    irn.client.loop_start()

    fld = irn.temp
    print(fld['tbnk'].when_activated)
    for i in range(10):
        sleep(1)
        print(fld['tbnk'].temperature)
    # fldi = FildReceptor()
    fldx = irn.complects
    fldx['cmp4'].switch.onoff(1)
    sleep(1)
    fldx['cmp4'].switch.onoff(0)
    sleep(1)
    fldx['cmp4'].switch.onoff('on')
    sleep(1)
    fldx['cmp4'].switch.onoff('off')
    sleep(1)
    fldx['cmp4'].switch.onoff('ON')
    sleep(1)
    fldx['cmp4'].switch.onoff('OFF')
    # fldx['cmp4'].switch.source = fld.sub['tbnk']
    # if fld.sub['tbnk'].is_active:
    #   print(fld.sub['tbnk'].temperature, fld.sub['tbnk'].value)
    pause()
