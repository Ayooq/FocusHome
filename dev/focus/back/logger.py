import logging


_formats_list = [
    '%(asctime)s %(name)s %(levelname)-11s %(message)s',
    '%(filename)-11s [LINE:%(lineno)d]  #%(levelname)-7s [%(asctime)s] %(message)s'
]

_file_formatter = logging.Formatter(_formats_list[0])
_stream_formatter = logging.Formatter(_formats_list[1])


def _set_file_handler(filename, level, formatter):
    fh = logging.FileHandler(filename)
    fh.setLevel(level)
    fh.setFormatter(formatter)

    return fh


def _set_stream_handler(level, formatter):
    sh = logging.StreamHandler()
    sh.setLevel(level)
    sh.setFormatter(formatter)

    return sh


def main_logger(filename, level=logging.INFO):
    """Создать и настроить головной регистратор.

    Параметры:
    \t:param filename: название файла, в который будет производиться запись.
    \t:param level: уровень логирования.
    """

    # Cоздать регистратор с названием 'FP' и присвоить ему указанный уровень логирования:
    logger = logging.getLogger('FP')
    logger.setLevel(level)

    # Наполнить словарь обработчиков событий:
    logger_handlers = {
        'file_handler': _set_file_handler(
            filename,
            logging.INFO,
            _file_formatter
        ),
        'stream_handler': _set_stream_handler(
            logging.DEBUG,
            _stream_formatter
        ),
    }

    # Добавить обработчики в регистратор:
    for handler in logger_handlers.values():
        logger.addHandler(handler)

    return logger
