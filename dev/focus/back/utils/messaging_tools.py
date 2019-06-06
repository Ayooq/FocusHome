def _log(instance, msg):
    """Зарегистрировать события согласно указанным уровням логирования."""

    instance.logger.debug(
        '%s %s | [%s]', instance.description, msg, repr(instance))
    instance.logger.info('%s %s', instance.description, msg)


def _report(instance, msg_type, msg_body):
    """Опубликовать сообщение о событии."""

    if msg_type:
        instance.reporter.set_type(msg_type, msg_body).report()
    else:
        instance.reporter.event(instance.description, msg_body).report()


def log_and_report(instance, msg_body, msg_type=None):
    """Опубликовать сообщение о событии и создать соответствующие записи в логе."""

    _log(instance, msg_body)
    _report(instance, msg_type, msg_body)


def register(instance, subscriber, callback):
    instance.reporter.register(subscriber, callback)


def unregister(instance, subscriber, callback):
    instance.reporter.unregister(subscriber)
