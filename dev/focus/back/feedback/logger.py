import logging
from typing import Type

Formatter = logging.Formatter
FileHandler = logging.FileHandler
StreamHandler = logging.StreamHandler

_formats_list = [
    '%(asctime)s %(name)s %(levelname)-7s %(message)s',
    '%(filename)-17s line:%(lineno)-5d %(levelname)-8s[%(asctime)s] %(message)s'
]


class Logger:
    """Головной регистратор событий.

    Параметры:
        :param filename: название файла, в который будет производиться запись;
        :param level: уровень логирования.

    Методы:
        :meth __init__(self, filename, level): — инициализировать экземпляр
    класса;
        :meth set_file_handler(self, filename, level, formatter): — установить
    обработчик для записи данных в файл;
        :meth set_stream_handler(self, level, formatter): — установить
    обработчик для записи данных в поток ввода/вывода;

    Свойства:
        :prop handlers(self): — словарь обработчиков данных.
    """

    def __init__(self, filename: str, level: int = logging.DEBUG) -> None:
        self.root = logging.getLogger()
        self.root.setLevel(level)

        self.dest = filename
        self.level = level

        self.file_formatter = logging.Formatter(_formats_list[0])
        self.stream_formatter = logging.Formatter(_formats_list[1])

        self.set_handlers()

    @classmethod
    def spawn_child(cls, name: str) -> logging.Logger:
        """Создать дочерний логгер."""
        return logging.getLogger(name)

    def set_handlers(self) -> None:
        fh = self._set_file_handler(self.dest, self.level, self.file_formatter)
        sh = self._set_stream_handler(self.level, self.stream_formatter)

        self.root.addHandler(fh)
        self.root.addHandler(sh)

    def _set_file_handler(
        self,
        filename: str,
        level: int,
        formatter: Formatter
    ) -> FileHandler:
        fh = FileHandler(filename)
        fh.setLevel(level)
        fh.setFormatter(formatter)

        return fh

    def _set_stream_handler(
            self, level: int, formatter: Formatter) -> StreamHandler:
        sh = StreamHandler()
        sh.setLevel(level)
        sh.setFormatter(formatter)

        return sh
