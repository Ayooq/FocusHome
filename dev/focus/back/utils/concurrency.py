from threading import Thread


class Worker:
    """Базовый организатор обработки данных через отдельный поток."""

    def __init__(self, worker):
        self.receiver_thread = Thread(target=worker, daemon=True)
        self.receiver_thread.start()

        self.message_received = 'Обработчик не установлен!'

    def set_message_callback(self, callback):
        self.message_received = callback

    def quit(self):
        self.receiver_thread.join()
