import logging


_formats_list = [
    '%(asctime)s %(name)s %(levelname)-11s %(message)s',
    '%(filename)-11s [LINE:%(lineno)d]  #%(levelname)-7s [%(asctime)s] %(message)s'
]


class Logger:
    """Головной регистратор.

    Параметры:
    \t:param filename: название файла, в который будет производиться запись;
    \t:param level: уровень логирования.
    """

    def __init__(self, filename, level=logging.INFO, prefix='FocusPro'):
        self.dest = filename
        self.level = level
        self.prefix = prefix

        self.instance = logging.getLogger(self.prefix)
        self.instance.setLevel(self.level)

        self._file_formatter = logging.Formatter(_formats_list[0])
        self._stream_formatter = logging.Formatter(_formats_list[1])

        for handler in self.handlers.values():
            self.instance.addHandler(handler)

    @property
    def handlers(self):
        return {
            'file_handler': self._set_file_handler(
                self.dest,
                self.level,
                self._file_formatter
            ),
            'stream_handler': self._set_stream_handler(
                logging.DEBUG,
                self._stream_formatter
            ),
        }

    def _set_file_handler(self, filename, level, formatter):
        fh = logging.FileHandler(filename)
        fh.setLevel(level)
        fh.setFormatter(formatter)

        return fh

    def _set_stream_handler(self, level, formatter):
        sh = logging.StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(formatter)

        return sh
