import operator
from ast import literal_eval
from typing import Dict, List, NoReturn, Tuple, Type, Union

from ..utils.messaging import notify


class Parser:
    """Парсер поступающих инструкций."""

    def parse_instructions(
            self,
            device: Type[object],
            payload: dict,
    ) -> Dict[str, list]:
        """Разбить инструкции на составляющие для последующей обработки.

        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro
        :param payload: словарь с инструкциями, который нужно распарсить
        :type payload: dict

        :return: словарь, содержащий распарсенные инструкции
        :rtype: dict[str, list]
        """
        routine_id = str(payload.get('routine_id'))
        instructions = {'routines': {}, 'commands': []}

        for k, v in payload['instruction'].items():
            if k == 'routine':
                command = self.parse_actions(v.get('actions'))
                print('parsed command:', command)

                if (conditions := v.get('conditions')):
                    conditions = self.parse_conditions(device, conditions)
                    instructions['routines'][routine_id] = conditions, command
                    print('routines:', instructions['routines'])
                else:
                    instructions['commands'].append(command)

        return instructions

    def parse_actions(self, actions: List[dict]) -> List[list]:
        """Распарсить список действий для переданной рутины.

        :param actions: список заданных действий
        :type actions: list[dict]

        :return: вложенный список распарсенных действий
        :rtype: list[list]
        """
        parsed_actions = []

        for act in actions:
            callback = act.get('function', 'set_state')
            value = act['value']

            if callback in ('sleep', 'timeout', 'wait', 'watch', 'monitor'):
                async_ = True
            else:
                async_ = False

            if value:
                target = act['unit']
                kwargs = {'value': value}
                parsed_actions.append([target, callback, async_, kwargs])

                continue

            target, kwargs = [], {}

            for i in act.get('params'):
                if i['name'] == 'unit':
                    unit = i['value']
                    target.append(unit)
                else:
                    kwargs.update({i['name']: i['value']})

            parsed_actions.append([target, callback, async_, kwargs])

        return parsed_actions

    @classmethod
    def parse_conditions(
            cls,
            device: Type[object],
            conditions: List[Union[list, dict, str]],
    ) -> str:
        """Рекурсивно распарсить условия выполнения рутины.

        Обрабатываются три типа данных: словарь (1), строка (2) и список (3).
        1) содержит данные для формирования операции сравнения переданного
        значения с текущим состоянием компонента;
        2) добавляется в результирующий список для вычислений как оператор
        логического выражения;
        3) инициирует вызов этой же функции рекурсивно с собой в качестве
        аргумента.

        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro
        :param conditions: список условий для проверки на истинность
        :type conditions: list

        :return: выражение для проверки условий в виде строки
        :rtype: str
        """
        res = []
        
        for c in conditions:
            if isinstance(c, list):
                c = cls.parse_conditions(device, c)
            elif isinstance(c, dict):
                unit_id, op, val = c['unit'], c['compare'], c['value']
                c = f'${unit_id}:{op}:{val}'
            elif c.startswith('$'):
                unit_id, op, val = c.strip('$').split(':')
                unit_obj = cls.id_to_object(unit_id, device)
                op = cls.get_operator_method(op, device)
                val = cls.get_evaluated_value(val)
                c = str(op(unit_obj.state, val))

            res.append(c)

        return ' '.join(res)

    @staticmethod
    def id_to_object(
            id_: str, device: Type[object]) -> Union[Type[object], None]:
        """Преобразовать строковый идентификатор в экземпляр объекта.

        :param id_: строковый идентификатор компонента
        :type id_: str
        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro

        :return: экземпляр объекта устройства/компонента либо None
        :rtype: object or None
        """
        if id_ == 'self':
            return device

        for group_families in device.hardware.values():
            for family_components in group_families.values():
                if id_ in family_components:
                    return family_components[id_]

        return None

    @classmethod
    def get_command(
            cls,
            registry: Type[object],
            cmd: str,
            device: Type[object],
    ) -> Union[str, NoReturn]:
        """Получить рабочий метод из реестра команд соответственно переданному
        названию команды.

        :param registry: реестр команд
        :type registry: focus.back.commands.handle.CommandsRegistry
        :param cmd: название команды
        :type cmd: str
        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro

        :raise AttributeError: команда отсутствует в реестре

        :return: метод класса реестра
        :rtype: str
        """
        try:
            meth = getattr(registry, cmd)
        except AttributeError:
            msg = 'команда отсутствует в реестре!'
            notify(device, msg, no_repr=True, report_type='warning')

            raise
        else:
            return meth

    @staticmethod
    def get_operator_method(
            op: str, device: Type[object]) -> Union[str, NoReturn]:
        """Получить рабочий метод из модуля operator соответственно переданному
        названию оператора сравнения.

        :param op: название оператора
        :type op: str
        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro

        :raise AttributeError: недопустимый оператор сравнения

        :return: метод сравнения
        :rtype: str
        """
        try:
            meth = getattr(operator, op)
        except AttributeError:
            msg = 'недопустимый оператор сравнения!'
            notify(device, msg, no_repr=True, report_type='warning')

            raise
        else:
            return meth

    @staticmethod
    def get_evaluated_value(value: str) -> Union[int, float, str]:
        try:
            value = literal_eval(value)
        except (ValueError, SyntaxError):
            pass
        finally:
            return value
