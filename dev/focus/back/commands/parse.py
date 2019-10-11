import operator
from ast import literal_eval
from typing import Dict, List, Tuple, Type, Union

from ..utils.messaging import notify


class Parser:
    """Парсер поступающих инструкций."""

    def parse_instructions(
            self,
            device: Type[object],
            payload: dict,
            hardware: Tuple[dict, dict],
    ) -> Dict[str, list]:
        """Разбить инструкции на составляющие для последующей обработки.

        :param device: экземпляр объекта устройства
        :type device: focus.back.FocusPro
        :param payload: словарь с инструкциями, который нужно распарсить
        :type payload: dict
        :param hardware: кортеж из семейств компонентов
        :type hardware: tuple[dict, dict]

        :return: словарь, содержащий распарсенные инструкции
        :rtype: dict[str, list]
        """
        routine_id = str(payload.get('routine_id'))
        instructions = {'routines': [], 'commands': []}

        for k, v in payload['instruction'].items():
            if k == 'routine':
                actions = v.get('actions')
                actions = self.parse_actions(actions)
                command = [routine_id, actions]

                conditions = v.get('conditions')

                if conditions:
                    components_objects = []
                    conditions = self.parse_conditions(
                        device, conditions, hardware, components_objects)
                    command.extend([conditions, components_objects])
                    instructions['routines'].append(command)
                else:
                    instructions['commands'].append(command)

        return instructions

    def parse_conditions(
            self,
            device: Type[object],
            conditions: List[Union[list, dict, str]],
            hardware: Tuple[dict, dict],
            components_objects: List[Type[dict]]
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
        :type device: dict
        :param conditions: список условий для проверки на истинность
        :type conditions: list
        :param hardware: кортеж из словарей компонентов
        :type hardware: tuple[dict, dict]
        :param components_objects: список для добавления экземпляров объектов
            компонентов устройства
        :type components_objects: list[dict]

        :return: составленное выражение для проверки условий в виде строки
        :rtype: str
        """
        expression = []

        for c in conditions:
            if isinstance(c, list):
                c = self.parse_conditions(
                    device, c, hardware, components_objects)
            elif isinstance(c, dict):
                op, unit, val = self.get_items_to_compare(device, c, hardware)
                c = f'${op}:{unit.id}:{val}'
                components_objects.append(unit)

            expression.append(c)

        return ' '.join(expression)

    def get_items_to_compare(
            self,
            device: Type[object],
            condition: dict,
            hardware: Tuple[dict, dict],
    ) -> Tuple[Union[str, None], Type[dict], Union[int, float, str]]:
        """Получить элементы для проверки логического выражения.

        :param device: экземпляр объекта устройства
        :type device: dict
        :param condition: условие для сравнения
        :type condition: dict
        :param hardware: кортеж из словарей компонентов
        :type hardware: tuple[dict, dict]

        :return: кортеж элементов выражения
        :rtype: tuple[str or None, dict, int or float or str]
        """
        op = self._get_operator_method(condition['compare'], device)
        unit = self._get_component(condition['unit'], hardware)
        val = self._get_evaluated_value(condition['value'])

        return op, unit, val

    @staticmethod
    def parse_actions(
            actions: List[dict]) -> List[Tuple[str, str, Dict[str, str]]]:
        """Распарсить список действий для переданной рутины.

        :param actions: список действий
        :type actions: list[dict]

        :return: список кортежей распарсенных действий
        :rtype: list[tuple]
        """

        parsed_actions = []

        for a in actions:
            components = a['params'].pop('components', None) or [a['unit']]
            callback = a['function']
            kwargs = {}

            for i in a['params']:
                kwargs.update({i['name']: i['value']})

            parsed_actions.append((components, callback, kwargs))

        return parsed_actions

    @classmethod
    def _get_operator_method(
            cls, op: str, device: Type[dict]) -> Union[str, None]:
        meth = f'operator.{op}'

        try:
            eval(meth)
        except AttributeError:
            msg = 'недопустимый оператор сравнения!'
            notify(device, msg, no_repr=True, report_type='warning')
        else:
            return meth

    @classmethod
    def _get_component(
            cls, target: str, hardware: Tuple[dict, dict]) -> Type[dict]:
        for group_families in hardware.values():
            for family_components in group_families.values():
                if target in family_components:
                    return family_components[target]

        return None

    @classmethod
    def _get_evaluated_value(cls, value: str) -> Union[int, float, str]:
        try:
            value = literal_eval(value)
        except (ValueError, SyntaxError):
            pass

        return value
