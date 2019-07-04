def log_and_report(instance, msg_body, msg_type='event', qos=1, retain=False):
    """Записать сообщение в журнал событий и отправить отчёт посреднику.

    Параметры:
      :param instance: — экземпляр объекта отправителя;
      :param msg_body: — тело сообщения;
      :param msg_type: — тип сообщения;
      :param qos: — уровень доставки сообщения посреднику, от 0 до 2;
      :param retain: — булевый показатель сохранения сообщения в качестве
    последнего "надёжного", выдаваемого сразу при подписке на данную тему.
    """

    common_args = instance, str(msg_body)
    report_args = msg_type, qos, retain

    _log(*common_args)
    _report(*common_args, *report_args)


def _log(instance, message: str):
    instance.logger.debug(
        '%s %s | [%s]', instance.description, message, repr(instance))
    instance.logger.info('%s %s', instance.description, message)


def _report(instance, msg_body: str, msg_type: str, qos: int, retain: bool):
    gpio_args = instance.pin, instance.description
    content = msg_type, msg_body, qos, retain, gpio_args

    instance.reporter._formalize(content)
    instance.reporter.report()


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
