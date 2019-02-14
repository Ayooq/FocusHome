import logging
import json
from threading import Thread
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
        'tcpu': {
                'pin': F_INTERNAL,
                'description': 'Процессор'
                },
        'tbnk': {
                'pin': 4,
                'description': 'Датчик'
                },
        'out1': {'pin': 5, 'description': 'Выход 1'},
        'cnt1': {'pin': 6, 'description': 'Контроль 1', 'pull_up': cnt_pull},
        'out2': {'pin': 13, 'description': 'Выход 2'},
        'cnt2': {'pin': 19, 'description': 'Контроль 2', 'pull_up': cnt_pull},
        'out3': {'pin': 26, 'description': 'Выход 3'},
        'cnt3': {'pin': 12, 'description': 'Контроль 3', 'pull_up': cnt_pull},
        'out4': {'pin': 16, 'description': 'Выход 4'},
        'cnt4': {'pin': 20, 'description': 'Контроль 4', 'pull_up': cnt_pull},
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

finput = [
        'cnt1', 'cnt2', 'cnt3', 'cnt4',
        'input1', 'input2', 'input3', 'input4', 'input5',
]

foutput = [
        'out1', 'out2', 'out3', 'out4',
        'led1', 'led2',
]


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
        return "%s(description=%r, pin=%r, id=%r, device=%r)" % (
                self.__class__.__name__,
                self.description,
                self.pin,
                self.ident,
                self.device
                )


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


class TemperatureSensor(CPUTemperature):
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


class GReceptorT(GIron):
    '''Датчики Температуры'''

    def __init__(self, **kwargs):
        GIron.__init__(self, CPUTemperature, **kwargs)
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        # self.device = LED(self.pin)
        self.reporter = Reporter(self.ident)
        self.logger.debug('Подготовка %s' % repr(self))
        self.value = None

    def get(self):
        ''' TODO: Проверка на существование'''
        cpu = CPUTemperature(
                min_temp=self.mini,
                max_temp=self.maxi)
        self.value = cpu.temperature


class GSwitch(GIron):
    '''Выключатель как LED'''
    def __init__(self, **kwargs):
        GIron.__init__(self, LED, **kwargs)
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.reporter = Reporter(self.ident)
        self.logger.debug('Подготовка %s' % repr(self))

    def on(self):
        '''Switch ON'''
        self.device.on()
        self.logger.info(u'%s [%s]' % (self.on.__doc__, repr(self)))
        self.reporter.warning(self.description, 'ВКЛ').public()

    def off(self):
        '''Switch OFF'''
        self.device.off()
        self.logger.info(u'%s [%s]' % (self.off.__doc__, repr(self)))
        self.reporter.event(self.description, 'ОТКЛ').public()

    def onoff(self, value):
        if value:
            self.on()
        else:
            self.off()


class FildReceptor(object):
    ''''''
    def __init__(self, lst):

        self.receptors = [
            GReceptor(ident=key, **firons[key]) for key in lst]

        self.subscribe(self.dumper)

    def subscribe(self, function):
        for rec in self.receptors:
            rec.reporter.registre('route', function)

    def dumper(self, report):
        '''тестовый вывод'''
        print(u'Печатаю', json.dumps(report, ensure_ascii=True))


class GReceptor(GIron):
    '''Концевой датчик как кнопка'''
    def __init__(self, **kwargs):
        GIron.__init__(self, Button, **kwargs)
        self.logger = logging.getLogger('cfactory.%s' % __name__)
        # self.enable_mock()
        self.gwait = False
        self.state = False
        self.interval = 2.0
        self.gwait = False
        self.device.when_pressed = self.on
        if 'cnt' in self.ident:
            self.device.when_released = self.off
        else:
            self.device.when_released = self.off
        # Через Reporter идет связка обмена данными
        self.reporter = Reporter(self.ident)
        self.logger.debug('Подготовка %s' % repr(self))

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
        self.logger.info(u'%s [%s]' % (self.on.__doc__, repr(self)))
        self.reporter.warning(self.description, 'ВКЛ').public()

    def offf(self):
        '''filter released'''
        self.logger.debug(
            u'%s w=%s [%s]' %
            (self.offf.__doc__, self.gwait, repr(self))
        )
        self.gwait = False
        if self.device.is_pressed:
            self.state = True
            return
        else:
            self.state = False
            self.rptoff()

    def off(self):
        '''Button released'''
        if self.device.is_pressed:
            self.state = True
            return
        self.state = False
        self.logger.info(u'%s [%s]' % (self.off.__doc__, repr(self)))
        self.reporter.event(self.description, 'ОТКЛ').public()

    def foff(self):
        '''start timer '''
        # self.logger.debug(u'%s [%s]' % (self.foff.__doc__, self.gwait))
        if self.gwait:
            self.state = False
            return
        self.logger.debug(u'%s [%s]' % (self.foff.__doc__, self.gwait))
        self.gwait = True


if __name__ == '__main__':

    from signal import pause
    from candle import create_logger

    logger = create_logger(logging.DEBUG)
    logger.info('test util')
    fld = FildReceptor(finput)
    pause()
