from django.db import connection, transaction


class BaseModel:
    # data = None
    # id = None

    def __init__(self, id=None):
        self.cursor = connection.cursor()
        self.transaction = transaction
        self.id = int(id) if id else None
        self.data = self.get()

    def __del__(self):
        pass#self.cursor.close()

    def __getattr__(self, attr):
        if not attr == 'data':
            if attr in self.data:
                return self.data[attr]

    def __setattr__(self, attr, value):
        if attr != 'data':
            if type(self.data) == dict:
                if attr in self.data:
                    self.data[attr] = value
                    return None

        super.__setattr__(self, attr, value)


    def to_dict(self):
        return self.data
