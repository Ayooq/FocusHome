import logging
import json
from threading import Thread
from time import sleep
# from threading import Timer

from gpiozero import CPUTemperature
from gpiozero import Button
from gpiozero import LED

from gpiozero import Device
from gpiozero.pins.mock import MockFactory

from report import Reporter


cnt_pull = True
F_INTERNAL = 0

firons = {
        'banka': {
                'id': 12345,
                'description': ' Адрес: ул. 20 лет РККА 105/17'
                },
        'tcpu': {
                # Все по умолчанию
                # 'sensor_file':',
                # 'min_temp':,
                # 'max_temp':,
                # 'theshold':,
                'description': 'Процессор'
                },
        'tbnk': {
                'sensor_file': '/sys/bus/w1/devices/28-0317232a55ff/w1_slave',
                'min_temp': 20.0,
                'max_temp': 40.0,
                'threshold': 25.0,
                'description': 'Датчик'
                },
        'out1': {'pin': 5, 'description': 'Розетка 1'},
        'cnt1': {'pin': 6, 'description': 'Контроль 1'},
        'out2': {'pin': 13, 'description': 'Розетка 2'},
        'cnt2': {'pin': 19, 'description': 'Контроль 2'},
        'out3': {'pin': 26, 'description': 'Розетка 3'},
        'cnt3': {'pin': 12, 'description': 'Контроль 3'},
        'out4': {'pin': 16, 'description': 'Розетка 4'},
        'cnt4': {'pin': 20, 'description': 'Контроль 4'},
        'input1': {'pin': 21, 'description': 'Вxoд 1'},
        'input2': {'pin': 18, 'description': 'Вход 2'},
        'input3': {'pin': 23, 'description': 'Вход 3'},
        'input4': {'pin': 24, 'description': 'Вход 4'},
        'input5': {'pin': 25, 'description': 'Вход 5'},
        'led1': {
            'pin': 17,
            'description': 'Светодиод 1',
            'active_high': False},
        'led2': {
            'pin': 27,
            'description': 'Светодиод 2',
            'active_high': False}
}

ftemp = ['tcpu', 'tbnk']

fallinput = [
        'cnt1', 'cnt2', 'cnt3', 'cnt4',
        'input1', 'input2', 'input3', 'input4', 'input5',
]

falloutput = [
        'out1', 'out2', 'out3', 'out4',
        'led1', 'led2',
]

finput = [
        'input1', 'input2', 'input3', 'input4', 'input5'
]

fled = [
        'led1', 'led2'
]

fcomplect = [
    {'cmp1': ('out1', 'cnt1')},
    {'cmp2': ('out2', 'cnt2')},
    {'cmp3': ('out3', 'cnt3')},
    {'cmp4': ('out4', 'cnt4')},
]


class Worker(object):
    '''Базовый организатор обмена
    Запускает обмен как поток. Устанавливает обработчик принятых сообщений
    '''
    def __init__(self, worker):
        self.logger = logging.getLogger('cfactory.%s' % __name__)
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
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.reporter = Reporter(self.ident)
        self.logger.debug('Подготовка %s [%s]' % (self.ident, repr(self)))

    @property
    def state(self):
        return self.device.is_lit

    def on(self):
        '''Switch ON'''
        self.device.on()
        self.public(self.on.__doc__, 'ВКЛ')
        # self.logger.info(u'%s [%s]' % (self.on.__doc__, repr(self)))
        # self.reporter.warning(self.description, 'ВКЛ').public()

    def off(self):
        '''Switch OFF'''
        self.device.off()
        self.public(self.off.__doc__, 'ОТКЛ')
        # self.logger.info(u'%s [%s]' % (self.off.__doc__, repr(self)))
        # self.reporter.event(self.description, 'ОТКЛ').public()

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
        self.logger.info(
            u'%s %s [%s]' %
            (self.ident, log_info, repr(self))
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


class W1Temperature(CPUTemperature):
    @property
    def temperature(self):
        # with io.open(self.sensor_file, 'r') as f:
        with open(self.sensor_file, 'r') as f:
            return float(f.readlines()[1].split("=")[1]) / 1000


class TemperatureCPU(object):
    '''Температура ЦПУ'''

    def __init__(self, **kwargs):
        self.mini = kwargs.get('min', None)
        self.mini = kwargs.get('max', None)
        self.value = None

    def get(self):
        ''' TODO: Проверка на существование'''
        cpu = CPUTemperature(
                min_temp=self.mini,
                max_temp=self.maxi)
        self.value = cpu.temperature


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
        # with io.open(self.sensor_file, 'r') as f:
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

    def public(self, log_info, message):
        self.logger.info(
            u'%s %s [%s]' %
            (self.ident, log_info, repr(self))
        )
        self.reporter.event(log_info, message).public()
        # self.reporter.event(self.description, message).public()


class GControlSwitch(object):
    ''''''
    def __init__(self, id_switch, id_recep, **kwargs):
        self.ident = kwargs.pop('ident', None)
        self.switch = GSwitch(ident=id_switch, **firons[id_switch])
        self.recept = GReceptor(True, ident=id_recep, **firons[id_recep])
        self.sub = [self.switch, self.recept]
        self.value = False
        self.recept.addcallbacks(self.switchon, self.switchoff)

    def subscribe(self, function):
        self.switch.reporter.registre('route', function)
        self.recept.reporter.registre('route', function)

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
        '''Control ON'''
        if self.value:
            return
        if self.switch.device.is_lit:
            self.value = True
            self.recept.state = True
            self.recept.public(self.switchon.__doc__, 'ON')

    def switchoff(self):
        '''Control OFF'''
        if self.switch.device.is_lit:
            return
        self.value = False
        self.recept.state = False
        self.recept.public(self.switchoff.__doc__, 'OFF')


class GReceptor(GIron):
    '''Концевой датчик'''
    def __init__(self, external_callback=False, **kwargs):
        GIron.__init__(self, Button, **kwargs)
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        # self.enable_mock()
        self.gwait = False
        self.state = False
        self.interval = 2.0
        self.gwait = False
        if not external_callback:
            self.addcallbacks(self.on, self.off)
        # Через Reporter идет связка обмена данными
        self.reporter = Reporter(self.ident)
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
        '''Button pressed'''
        if self.state:
            return
        self.state = True
        if self.gwait:
            return
        self.public(self.on.__doc__, 'ON')

    def off(self):
        '''Button released'''
        if self.device.is_pressed:
            self.state = True
            return
        self.state = False
        self.public(self.off.__doc__, 'OFF')

    def public(self, log_info, message):
        self.logger.info(
            u'%s %s [%s]' %
            (self.ident, log_info, repr(self))
        )
        self.reporter.event(self.description, message).public()


class Fild2(object):
    '''Cписок'''
    def __init__(self, posev, lst):
        self.sub = {}
        for d in lst:
            it = tuple(d.items())
            key, item = it[0]
            self.sub[key] = posev(ident=key, *item)
        self.subscribe(self.dumper)

    def subscribe(self, function):
        for rec in self.sub.keys():
            # print(self.sub[rec])
            self.sub[rec].subscribe(function)

    def dumper(self, report):
        '''тестовый вывод'''
        print(u'Печатаю', json.dumps(report, ensure_ascii=False))

    def keys(self):
        return self.sub.keys()

    def __getitem__(self, pos):
        return self.sub[pos]


class Fild(object):
    '''Cписок'''
    def __init__(self, posev, lst):

        self.sub = {key: posev(ident=key, **firons[key]) for key in lst}
        self.subscribe(self.dumper)

    def subscribe(self, function):
        for rec in self.sub:
            self.sub[rec].reporter.registre('route', function)

    def dumper(self, report):
        '''тестовый вывод'''
        print(u'Печатаю', json.dumps(report, ensure_ascii=False))

    def keys(self):
        return self.sub.keys()

    def __getitem__(self, pos):
        return self.sub[pos]


class FildComplect(Fild2):
    '''Список комплектов'''
    def __init__(self):
        Fild2.__init__(self, GControlSwitch, fcomplect)


class FildSwitch(Fild):
    '''Список выходов'''
    def __init__(self):
        Fild.__init__(self, GSwitch, falloutput)


class FildLed(Fild):
    '''Список выходов'''
    def __init__(self):
        Fild.__init__(self, GSwitch, fled)


class FildReceptor(Fild):
    '''Список входов'''
    def __init__(self):
        Fild.__init__(self, GReceptor, finput)


class FildTemperature(Fild):
    '''Список датчиков температуры'''
    def __init__(self):
        Fild.__init__(self, GTemperature, ftemp)


if __name__ == '__main__':

    def hot():
        print('HOOOOOOOOT')

    from signal import pause
    from time import sleep
    from candle import create_logger

    logger = create_logger(logging.DEBUG)
    logger.info('test util')
    fld = FildTemperature()
    print(fld.sub['tbnk'].when_activated)
    for i in range(10):
        sleep(1)
        print(fld.sub['tbnk'].temperature)
    # fldi = FildReceptor()
    fldx = FildComplect()
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
    fldx['cmp4'].switch.source = fld.sub['tbnk']
    if fld.sub['tbnk'].is_active:
        print(fld.sub['tbnk'].temperature, fld.sub['tbnk'].value)
    pause()
