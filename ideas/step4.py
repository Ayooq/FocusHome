#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  step3.py
#
#  Copyright 2019 Developer <devel@raspberrypi>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.


import logging
import candle.face as cf
from candle import create_logger
import tkinter as tk
import tkinter.ttk as ttk

from gpiozero import CPUTemperature
# from gpiozero import Button
# from gpiozero import Device
# from gpiozero.pins.mock import MockFactory
from random import choice

from gpio_iron import firons, finput, foutput
from gpio_iron import GReceptor
from gpio_iron import GSwitch
from gpio_iron import TemperatureSensor


class IndicatorTemperature(object):

    def __init__(self, master, name, value):
        self.variable = tk.StringVar()
        label = "Температура " + name
        self.indicator = cf.Indicator(
            master,
            label,      # Заголовок индикатора
            self.variable,   # Текстовая переменая данных
            ndigit=5,       # максимальная ширина индикатора
            unit='°C'      # суффикс параметра
        )
        self.variable.set(value)


class Temperaturs(ttk.Frame):
    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.indicators = {}
        self._init_indi()
        self.device_folder = '/sys/bus/w1/devices/28-0317232a55ff'
        self.after_idle(self.tick)

    def _init_indi(self):
        row = 0
        name = "Процессор"
        current = "0.0"

        widget = IndicatorTemperature(self, name, current)
        self.indicators.setdefault(name, widget)
        widget.indicator.grid(row=row, column=0, sticky='wens')

        widget = IndicatorTemperature(self, 'Датчик', current)
        self.indicators.setdefault('Датчик', widget)
        widget.indicator.grid(row=row, column=1, sticky='wens')

    def new_init_sensors(self):
        # for key in ftemp:
            # g
        name = "Процессор"
        cpu = CPUTemperature(min_temp=50, max_temp=90)
        self.indicators[name].variable.set(cpu.temperature)
        name = "Датчик"
        device_file = self.device_folder + '/w1_slave'
        inside = TemperatureSensor(device_file)
        self.indicators[name].variable.set(inside.temperature)

    def _init_sensors(self):
        name = "Процессор"
        cpu = CPUTemperature(min_temp=50, max_temp=90)
        self.indicators[name].variable.set(cpu.temperature)
        name = "Датчик"
        device_file = self.device_folder + '/w1_slave'
        inside = TemperatureSensor(device_file)
        self.indicators[name].variable.set(inside.temperature)

    def get_t(self):
        name = "Процессор"
        cpu = CPUTemperature(min_temp=50, max_temp=90)
        self.indicators[name].variable.set(cpu.temperature)
        name = "Датчик"
        device_file = self.device_folder + '/w1_slave'
        inside = TemperatureSensor(device_file)
        self.indicators[name].variable.set(inside.temperature)

    def tick(self):
        self.after(2000, self.tick)
        self.get_t()


class ViewSensor(object):
    '''Строка таблицы как индикатор'''

    def __init__(self, number, table):

        self.logger = logging.getLogger('cfactory.%s' % __name__)
        self.number = number
        self.table = table

    def frmt(self, rpt):
        '''Функция обновления
        Через механизм Rеport

        '''
        self.table.add(self.number, rpt)


class VSwitch(ttk.Checkbutton):
    ''' Checkbutton c
    инициализационное сообщение
    '''
    def __init__(self, frm, label):
        options = {
            'cursor': 'hand2',
            # 'command': self.message
        }
        self.variable = tk.IntVar()
        ttk.Checkbutton.__init__(
            self, frm, text=label,
            variable=self.variable,
            style='Ikra.TCheckbutton',
            **options
        )

    def message(self):
        tk.messagebox.showinfo(u"Извините", u"Еще не готово", parent=self)


class Paketnic(ttk.Frame):

    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
    # Элементы в теле в одну коолонку
        self.columnconfigure(0, weight=1)
        self.devs = [
                        MSwitch(self, ident=key, **firons[key])
                        for key in foutput]

        for pos, dev in enumerate(self.devs):
            self.rowconfigure(pos, weight=1)  # Эти колонки масштабируюся
            dev.widget.grid(
                row=pos,
                column=0,
                sticky=tk.W + tk.E + tk.N + tk.S  # Дабы изменяло размер
            )
            # self.widgets.setdefault(key, kl)


class MSwitch(object):
    '''реле/светодиод с GUI'''
    def __init__(self, master, **kwargs):
        self.iron = GSwitch(**kwargs)
        self.widget = VSwitch(master, self.iron.ident)
        self.widget.configure(command=self.cb)

    def cb(self):
        val = self.widget.variable.get()
        self.iron.onoff(val)


class MTemperature(object):
    '''датчики температуры с Индикатором'''
    pass
    # self.iron =


class TestControl(object):
    '''Связка МОДЕЛЬ КОНТРОЛЛЕР'''
    def __init__(self, master):
        pass


class TestForma(object):
    '''Связка МОДЕЛЬ ОТОБРАЖЕНИЕ'''

    def __init__(self, master):
        self.list_sensors = finput
        self.sensors = {}
        self.vsensors = {}
        self.font2 = 'courier 12 bold'
        self.font1 = 'courier 12 italic'
        self.number = len(self.list_sensors) + 1
        self.table = cf.Table(master, rows=self.number)
        # self.p.grid(sticky = 'wens')
        self._init_0_row()
        self.table.column_font(2, self.font2)
        self.table.column_font(1, self.font1)
        self._init_sensors()
        # self.tst2()

    def _init_0_row(self):
        '''Раскраска'''
        self.table.row_bg(0, 'yellow')        # красим строчку
        self.table.column_bg(0, 'yellow')    # красим колонку

    def _init_sensors(self):
        '''Начальная установка ячейки'''
        for pos, key in enumerate(self.list_sensors):
            n_line = pos + 1
            sns = GReceptor(ident=key, **firons[key])
            vsns = ViewSensor(n_line, self.table)
            sns.reporter.registre('ta', vsns.frmt)
            self.sensors.setdefault(key, sns)
            self.vsensors.setdefault(key, vsns)

    def test(self):
        name_sensor = choice(list(self.sensors.keys()))
        self.sensors[name_sensor].test()


class TestApp(cf.Face):

    # Секция событий
    def __init__(self, *args, **kwargs):
        cf.Face.__init__(self, *args, **kwargs)
        self.body.rowconfigure(1, weight=1)
        # self.body.columnconfigure(0, weight=1)
        # user_tools = [('put', 'сюда', self.p2.test), ]
        # self.add_tools(user_tools)
        self.add_tools()

    def _create_widgets(self):
        self.p1 = Temperaturs(self.body)
        self.p1.grid(row=0, column=0, sticky='wens')
        self.p2 = TestForma(self.body)
        self.p2.table.grid(row=1, column=0, sticky='wens')

        self.p3 = Paketnic(self.body)
        self.p3.grid(row=1, column=1, sticky='wens')
        # devouts = [CheckSwitch(**IRON[key]) for key in BOOL_OUT]

        # lst_function = (
        #   (u'Tест\ncобытия', self._tst_lamps),
        #   (u'Тест\nвыборки', self._tst_select),
        #   (u'КОЛА', None),
        #   (u'КВАС', None),
        # )
        # self.menu = Packet(self.body, lst_function)
        # self.menu.grid(sticky='wens')
        # pass


def main(args):
    logger = create_logger(logging.DEBUG)
    logger.info('test util')
    kwargs = {'symbol': 'T1', 'name': 'Обслуживание'}
    TestApp(**kwargs).mainloop()
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
