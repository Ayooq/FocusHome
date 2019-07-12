def register(instance, subscriber: str, callback):
    """Прокси для метода регистрации подписчика у экземпляра репортёра.

    Параметры:
      :param instance: — экземпляр класса, от чьего имени осуществляется
    отправка отчётов;
      :param subscriber: — имя подписчика, которому будут отправляться отчёты;
      :param callback: — обработчик отправляемых сообщений.
    """

    instance.reporter.register(subscriber, callback)


def unregister(instance, subscriber: str):
    """Прокси для метода удаления подписчика у экземпляра репортёра.

    Параметры:
      :param instance: — экземпляр класса, от чьего имени осуществляется
    отправка отчётов;
      :param subscriber: — имя подписчика, которого следует удалить из списка
    рассылки сообщений о событиях.
    """

    instance.reporter.unregister(subscriber)


def log_and_report(
    instance, msg, swap=False, type_='event', qos=1, retain=False
):
    """Записать сообщение в журнал событий и отправить отчёт посреднику.

    Параметры:
      :param instance: — экземпляр объекта отправителя;
      :param msg: — тело сообщения;
      :param swap: — флаг, определяющий позицию аргументов при логировании;
      :param type_: — тип сообщения;
      :param qos: — уровень доставки сообщения посреднику, от 0 до 2;
      :param retain: — булевый показатель сохранения сообщения в качестве
    последнего "надёжного", выдаваемого сразу при подписке на данную тему.
    """

    common_args = instance, str(msg)
    report_args = type_, qos, retain

    _log(*common_args, swap)
    _report(*common_args, *report_args)


def _log(instance, msg: str, swap: bool):
    args = [msg, instance.description] if swap else [instance.description, msg]
    debug_msg = '{}: {} | [{}]'.format(*args, repr(instance))
    instance.logger.debug(debug_msg)
    instance.logger.info(': '.join(args))


def _report(instance, msg: str, type_: str, qos: int, retain: bool):
    content = instance.id, type_, msg, qos, retain

    instance.reporter._formalize(content)
    instance.reporter.report()
