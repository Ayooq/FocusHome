from django.db import models
# from Profiles.models import Profiles


class Clients(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False,
    )

    def __str__(self):
        return self.name

    @staticmethod
    def get_clients_list(request):
        clients_list = []

        if request.user.has_perm('Clients.clients_list'):
            clients_list = Clients.objects.all()
        else:
            user_auth = Profiles.objects.get(auth_id=request.user.id)
            clients_list = Clients.objects.filter(client_id=user_auth.client_id)

        clients_list = list(clients_list.values('id', 'name'))

        if request.GET.get('all', None):
            clients_list.insert(0, {'id': 0, 'name': request.GET.get('all')})

        return list(clients_list)
