from threading import Thread


class Worker:
    """Базовый организатор обработки данных через отдельный поток.

    Параметры:
      :param service: — функция-обработчик, для исполнения которой
    требуется выделение отдельного потока;
      :param args: — опциональный кортеж аргументов для передачи
    функции-обработчику;
      :param kwargs: — опциональный словарь именованных аргументов для передачи
    функции-обработчику;

    Свойства:
      :attr receiver_thread: — объект выделенного потока;
      :attr message_received: — функция-обработчик для принятых сообщений.

    Методы:
      :meth set_message_callback: — установить функцию-обработчик для
    принятых сообщений;
      :meth quit: — завершить процесс, подождав, пока поток не будет уничтожен.
    """

    def __init__(self, service, *args, **kwargs):
        self.receiver_thread = Thread(
            target=service, daemon=True, args=args, kwargs=kwargs)
        self.receiver_thread.start()

        self.message_received = 'Обработчик не установлен!'

    def set_message_callback(self, callback):
        self.message_received = callback

    def quit(self):
        self.receiver_thread.join()
