"""Работа с исходящими сообщениями от устройства и его компонентов.

Функции:
    :func notify(
        component, msg, no_repr, local_only, report_type, qos, retain): — 
записать сообщение в журнал событий и отправить отчёт посреднику.
"""
from typing import Type, Union


def notify(
    component: Type[dict],
    msg: Union[int, str, float],
    no_repr: bool = False,
    local_only: bool = False,
    report_type: str = 'event',
    qos: int = 1,
    retain: bool = False
) -> None:
    """Записать сообщение в журнал событий и отправить отчёт посреднику.

    Параметры:
        :param component: — экземпляр объекта отправителя;
        :param msg: — тело сообщения;
        :param no_repr: — флаг, определяющий, из какой переменной будет браться
    имя компонента при логировании (установить в True, если сообщение исходит
    от самого устройства, иначе опустить данный аргумент при инициализации);
        :param local_only: — флаг отправки сообщений посреднику (в значении True
    не создаёт отчёт, ограничиваясь только локальным логированием);
        :param report_type: — тип отчёта;
        :param qos: — уровень доставки сообщения посреднику, от 0 до 2;
        :param retain: — булевый показатель сохранения сообщения в качестве
    последнего "надёжного", выдаваемого сразу при подписке на данную тему.
    """
    args = [component, msg]
    _log(*args, no_repr)

    if not local_only:
        args.extend([report_type, qos, retain])
        _report(*args)


def _log(
    component: Type[dict],
    msg: Union[int, str, float],
    no_repr: bool
) -> None:
    if no_repr:
        msg = ': '.join(['FocusPro', str(msg)])
    else:
        msg = f'{component.description} [{repr(component)}]: {msg}'

    component.logger.debug(msg)


def _report(
    component: Type[dict],
    msg: Union[int, str, float],
    report_type: str,
    qos: int,
    retain: bool
) -> None:
    content = component.id, report_type, msg, qos, retain

    component.reporter.fill_in(content)
    component.reporter.report()
