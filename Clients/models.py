from django.db import models
import Django.util as util
from Django.models import BaseModel
from django.db import connection, transaction


# class Clients(models.Model):
#     name = models.CharField(
#         max_length=255,
#         blank=False,
#         null=False,
#     )
#
#     class Meta:
#         db_table = 'clients'
#
#     def __str__(self):
#         return self.name
#
#     @staticmethod
#     def get_clients_list(request):
#         clients_list = []
#
#         if request.user.has_perm('Clients.clients_list'):
#             clients_list = Clients.objects.all()
#         else:
#             user_auth = 1 #Profiles.objects.get(auth_id=request.user.id)
#             clients_list = Clients.objects.filter(client_id=user_auth.client_id)
#
#         clients_list = list(clients_list.values('id', 'name'))
#
#         if request.GET.get('all', None):
#             clients_list.insert(0, {'id': 0, 'name': request.GET.get('all')})
#
#         return list(clients_list)


class Client(BaseModel):
    def get(self):
        if self.id:
            query = """
                SELECT
                      c.id as client_id
                    , c.name as client_name
                FROM clients as c
                WHERE c.id=%(client_id)s
            """
            self.cursor.execute(query, {
                "client_id": self.id
            })
            self.data = util.dictfetchone(self.cursor)
        else:
            self.data = {
                "client_id": 0,
                "client_name": ""
            }

        return self.data


# class Client(BaseModel):
#     client = None
#
#     def __init__(self, id=0):
#         self.client_id = int(id)
#         self.cursor = connection.cursor()
#
#         if self.client_id > 0:
#             self.client = self.get()
#
#     def __del__(self):
#         pass#self.cursor.close()
#
#     def get(self, id=0):
#         if self.client:
#             return self.client
#
#         if int(id) > 0:
#             self.client_id = int(id)
#
#         if self.client_id == 0:
#             return {
#                 "client_id": 0,
#                 "client_name": ""
#             }
#
#         query = """
#             SELECT
#                   c.id as client_id
#                 , c.name as client_name
#             FROM clients as c
#             WHERE c.id=%(client_id)s
#         """
#         self.cursor.execute(query, {
#             "client_id": self.client_id
#         })
#         self.client = util.dictfetchone(self.cursor)
#
#         return self.client
#
#     def __getattr__(self, key):
#         if key in self.client:
#             return self.client[key]
#
#     def toDict(self):
#         return self.client
#
#
def get_clients():
    clients = {}

    cursor = connection.cursor()
    query = """
        SELECT
              c.id as id
            , c.name as name
        FROM clients as c
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        clients[row[0]] = {
            'id': row[0],
            'name': row[1]
        }

    return clients
