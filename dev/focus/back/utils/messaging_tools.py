def _log(instance, msg):
    instance.logger.debug(
        '%s %s | [%s]', instance.description, msg, repr(instance))
    instance.logger.info('%s %s', instance.description, msg)


def _report(instance, msg_type, msg_body):
    if msg_type:
        instance.reporter._set_type(msg_type, msg_body).report()
    else:
        instance.reporter.event(instance.description, msg_body).report()


def log_and_report(instance, msg_body, msg_type=None):
    """Записать сообщение в журнал событий и отправить отчёт посреднику."""

    _log(instance, msg_body)
    _report(instance, msg_type, msg_body)


def register(instance, subscriber, callback):
    """Прокси для метода регистрации подписчика у экземпляра репортёра.

    Параметры:
        :object instance: — экземпляр класса, от чьего имени осуществляется
    отправка отчётов;
        :str subscriber: — имя подписчика, которому будут отправляться отчёты;
        :function callback: — обработчик отправляемых сообщений.
    """

    instance.reporter.register(subscriber, callback)


def unregister(instance, subscriber):
    """Прокси для метода удаления подписчика у экземпляра репортёра.

    Параметры:
        :object instance: — экземпляр класса, от чьего имени осуществляется
    отправка отчётов;
        :str subscriber: — имя подписчика, которого следует удалить из списка
    рассылки сообщений о событиях.
    """

    instance.reporter.unregister(subscriber)
