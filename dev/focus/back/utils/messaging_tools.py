def log_and_report(instance, msg_body, msg_type=None, qos=1, retain=False):
    """Записать сообщение в журнал событий и отправить отчёт посреднику."""

    _log(instance, msg_body)
    _report(instance, msg_type, msg_body, qos, retain)


def _log(instance, msg):
    instance.logger.debug(
        '%s %s | [%s]', instance.description, msg, repr(instance))
    instance.logger.info('%s %s', instance.description, msg)


def _report(instance, msg_body, msg_type='event', qos=1, retain=False):
    instance.reporter._formalize(msg_type, msg_body, qos, retain).report()


def register(instance, subscriber, callback):
    """Прокси для метода регистрации подписчика у экземпляра репортёра.

    Параметры:
        :param instance: — экземпляр класса, от чьего имени осуществляется
    отправка отчётов;
        :param subscriber: — имя подписчика, которому будут отправляться отчёты;
        :param callback: — обработчик отправляемых сообщений.
    """

    instance.reporter.register(subscriber, callback)


def unregister(instance, subscriber):
    """Прокси для метода удаления подписчика у экземпляра репортёра.

    Параметры:
        :param instance: — экземпляр класса, от чьего имени осуществляется
    отправка отчётов;
        :param subscriber: — имя подписчика, которого следует удалить из списка
    рассылки сообщений о событиях.
    """

    instance.reporter.unregister(subscriber)
