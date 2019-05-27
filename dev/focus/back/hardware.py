import logging
from time import sleep
from threading import Thread

import yaml
from gpiozero import LED, Button, CPUTemperature

from .logger import main_logger
from .report import Reporter
from .utils import Worker


def _log(instance, head, body):
    """Зарегистрировать события согласно указанным уровням логирования."""

    instance.logger.debug(
        '%s%s: %s | [%s]', head, instance.description, body, repr(instance))
    instance.logger.info('%s%s: %s', head, instance.description, body)


def _report(instance, msg_type, head, body):
    """Опубликовать сообщение о событии."""

    if msg_type:
        instance.reporter.set_type(msg_type, head, body).report()
    else:
        instance.reporter.event(instance.description, body).report()


def log_and_report(instance, head, body, msg_type=None):
    """Опубликовать сообщение о событии и создать соответствующие записи в логе."""

    _log(instance, head, body)
    _report(instance, msg_type, head, body)


class Layout:
    """Оборудование.

    Разбито на именованные группы.
    """

    def __init__(self, config_file='/home/pi/focus_pro/focus/config.yaml'):

        # Головной регистратор:
        self.logger = main_logger('/home/pi/focus_pro/focus/focus.log')

        # Заполнение словаря конфигурации на основе переданного файла.
        try:
            self.config = self.get_config(config_file)
        except Exception as e:
            self.logger.debug(
                'Ошибка в конфигурировании оборудования! [%s] [%s]', config_file, e)
            raise

        self.mk_units()

        self.logger.info('Запуск %s', self.ident)

    def get_config(self, config_file):
        """Загрузка описателя оборудования из файла конфигурации.

        :param str config_file: имя файла конфигурации для загрузки
        :rtype: `dict`

        .. warning::
            Конфигурационный файл должен быть доверительно проверен!
            Ссылки на имена классов позволяют выполнять произвольный код.
        """

        with open(config_file) as f:
            config_dict = yaml.load(f)

        return config_dict

    def mk_units(self):
        """Создать словарь компонентов на основе словаря конфигурации."""

        self.units = {}

        for group in self.config['units']:
            self.units[group] = self.set_context(self.config['units'][group])

    def set_context(self, group):
        """Установить контекст для компонентов единой группы."""

        group.pop('description', 'Нет описания')

        try:
            component = eval(group.pop('class', None))
            ctx = {unit: component(
                ident=unit, **group[unit]) for unit in group}
        except Exception:
            raise

        return ctx

    @property
    def ident(self):
        return self.config['device']['id']

    @property
    def delta(self):
        return self.config['device']['broker']['keepalive']

    @property
    def indicators(self):
        """Индикаторы."""

        return self.units['indicators']

    @property
    def inputs(self):
        """Входы."""

        return self.units['inputs']

    @property
    def complects(self):
        """Комплекты [Гнездо -- Контроль состояния]."""

        return self.units['complects']

    @property
    def temperature(self):
        """Температура."""

        return self.units['temperature']

    def quit(self):
        self.logger.info('Остановка работы %s', self.ident)


class FocusUnit:
    """Базовый класс для устройств GPIO."""

    def __init__(self, unit=None, **kwargs):
        self.pin = kwargs.pop('pin')
        self.ident = kwargs.pop('ident')
        self.description = kwargs.pop('description', None)

        try:
            self.unit = unit(self.pin, **kwargs)
        except:
            print(
                'Компонент не установлен! Необходимо указать класс компонента библиотеки gpiozero.')
            raise

        self.reporter = Reporter(self.ident)
        self.logger = logging.getLogger('FP.%s' % __name__)
        self.logger.debug('Подготовка %s [%s]', self.ident, repr(self))

    def __repr__(self):
        return '%s (%r, pin=%r, id=%r, description=%r)' % (
            self.__class__.__name__,
            self.unit,
            self.pin,
            self.ident,
            self.description,
        )

    def register(self, subscriber, callback):
        self.reporter.register(subscriber, callback)

    def unregister(self, subscriber):
        self.reporter.unregister(subscriber)


class FocusLED(FocusUnit):
    """Световой индикатор.

    Без логирования и публикации.
    """

    def __init__(self, **kwargs):
        super().__init__(unit=LED, **kwargs)

    @property
    def state(self):
        return not self.unit.is_lit

    def set_state(self, value):
        if value in ('ON', 'on', 1):
            self.off()
        else:
            self.on()

    def blink(self, *args, **kwargs):
        self.unit.blink(*args, **kwargs)

    def on(self):
        """Зажечь индикатор."""

        self.unit.off()

    def off(self):
        """Погасить индикатор."""

        self.unit.on()

    def toggle(self):
        """Изменить состояние индикатора."""

        self.unit.toggle()


class FocusSocket(FocusLED):
    """Гнездо (выходной разъём) со световым индикатором."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on(self):
        "Включить гнездо."

        super().on()
        log_and_report(self, '', 'включено')


    def off(self):
        "Отключить гнездо."

        super().off()
        log_and_report(self, '', 'отключено')


    def toggle(self):
        "Переключить гнездо."

        super().toggle()
        log_and_report(self, '', 'переключено')


class FocusReceptor(FocusUnit):
    """Концевой датчик (входной рецептор)."""

    def __init__(self, external_callback=False, **kwargs):
        super().__init__(unit=Button, **kwargs)
        self.lock = True

        if not external_callback:
            self.add_callbacks(self.on, self.off)

    def add_callbacks(self, func1, func2):
        self.unit.when_pressed = func1
        self.unit.when_released = func2

    @property
    def state(self):
        return self.unit.is_pressed

    def on(self):
        """Начать считывание входного сигнала."""

        if not self.lock and self.state:
            self.lock = True

            log_and_report(self, '', 'включён')

    def off(self):
        """Прервать считывание входного сигнала."""

        if self.lock and not self.state:
            self.lock = False

            log_and_report(self, '', 'отключён')


class FocusComplect:
    """Комплект [Гнездо -- Контроль состояния]."""

    def __init__(self, **kwargs):
        self.ident = kwargs.pop('ident')
        self.description = kwargs.pop('description', 'Комплект %s' % self.ident[-1])

        kout = kwargs.pop('out')
        kout['ident'] = self.ident + '/out'

        kcnt = kwargs.pop('cnt')
        kcnt['ident'] = self.ident + '/cnt'

        self.socket = FocusSocket(**kout)
        self.control = FocusReceptor(**kcnt)

        self.logger = logging.getLogger('FP.%s' % __name__)
        self.logger.debug('Подготовка %s [%s]', self.ident, repr(self))

        self.reporter = Reporter(self.ident)

    def __repr__(self):
        return '%s (id=%r, description=%r)' % (
            self.__class__.__name__,
            self.ident,
            self.description,
        )

    @property
    def state(self):
        return(self.socket.state, self.control.state)

    def on(self):
        """Включить гнездо."""

        if not self.control.lock:
            self.control.lock = True
            self.socket.on()

    def off(self):
        """Отключить гнездо."""

        if self.control.lock:
            self.control.lock = False
            self.socket.off()

    def register(self, subscriber, callback):
        self.socket.register(subscriber, callback)
        self.control.register(subscriber, callback)

    def unregister(self, subscriber):
        self.socket.unregister(subscriber)
        self.control.unregister(subscriber)


class FocusTemperature(CPUTemperature):
    """Датчик температуры."""

    def __init__(self, **kwargs):
        self.ident = kwargs.pop('ident')
        self.description = kwargs.pop('description', None)
        self.hysteresis = kwargs.pop('hysteresis', 0.0)
        self.delta = kwargs.pop('delta', 60)
        self._tick = self.delta

        super().__init__(**kwargs)

        self.logger = logging.getLogger('FP.%s' % __name__)
        self.logger.debug('Подготовка %s [%s]', self.ident, repr(self))

        self.reporter = Reporter(self.ident)

        Worker(self.threshold_monitor)

    def threshold_monitor(self):
        """Контроль за порогом срабатывания."""

        self.exceeded = False

        while True:
            sleep(1)

            if self._tick:
                self._tick -= 1
            else:
                log_and_report(self, 'Текущая температура ',
                               self.temperature, msg_type='info')
                self._tick = self.delta

            if self.is_active:
                if not self.exceeded:
                    log_and_report(self, 'Перегрев ',
                                   self.temperature, msg_type='warning')
                    self.exceeded = True
            else:
                if self.exceeded:
                    log_and_report(
                        self, 'Норма ', self.temperature)
                    self.exceeded = False

    def register(self, subscriber, function):
        self.reporter.register(subscriber, function)

    def unregister(self, subscriber):
        self.reporter.unregister(subscriber)


# class CPULoadAverage:
#     """Средняя загрузка ЦПУ."""

#     def __init__(self, **kwargs):
#         self.mini = kwargs.get('min', 0)
#         self.maxi = kwargs.get('max', 2)
#         self.value = None

#     def get_t(self):
#         """TODO: Проверка на существование."""
#         self.value = self.unit(
#             min_load=self.mini,
#             max_load=self.maxi)
