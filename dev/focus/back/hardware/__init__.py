import yaml

from ..utils import config_file_path, log_file_path, init_db, log_and_report, set_config
from ..logger import main_logger


class Hardware:
    """Оборудование.

    Разбито на именованные группы.
    """

    def __init__(self, config_file=config_file_path):

        # Головной регистратор:
        self.logger = main_logger(log_file_path)

        # Заполнение словаря конфигурации на основе переданного файла.
        try:
            self.config = self.get_config(config_file)
        except Exception as e:
            log_and_report(self, 'Ошибка в конфигурировании оборудования! [%s] [%s]' % (
                config_file, e), msg_type='error')

            raise

        self.conn = init_db('focus.db')
        set_config(self.conn, self.config)
        self.conn.close()

        self.make_units_dict()

    def get_config(self, config_file):
        """Загрузка описателя оборудования из файла конфигурации.

        :param str config_file: имя файла конфигурации для загрузки
        :rtype: `dict`

        .. warning::
            Конфигурационный файл должен быть доверительно проверен!
            Ссылки на имена классов позволяют выполнять произвольный код.
        """

        with open(config_file) as f:
            config_dict = yaml.load(f)

        return config_dict

    def make_units_dict(self):
        """Создать словарь компонентов на основе словаря конфигурации."""

        self.units = {}

        for group in self.config['units']:
            self.units[group] = self.set_context(self.config['units'][group])

    def set_context(self, group):
        """Установить контекст для компонентов единой группы."""

        group.pop('description', 'Нет описания')

        try:
            component = eval(group.pop('class', None))
            ctx = {unit: component(
                ident=unit, **group[unit]) for unit in group}
        except Exception:
            raise

        return ctx

    @property
    def ident(self):
        return self.config['device']['id']

    @property
    def delta(self):
        return self.config['device']['broker']['keepalive']

    @property
    def indicators(self):
        """Индикаторы."""

        return self.units['indicators']

    @property
    def inputs(self):
        """Входы."""

        return self.units['inputs']

    @property
    def complects(self):
        """Комплекты [Гнездо -- Контроль состояния]."""

        return self.units['complects']

    @property
    def temperature(self):
        """Температура."""

        return self.units['temperature']
