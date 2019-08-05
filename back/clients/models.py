from django.db import models
from django.template.context_processors import request


class Client(models.Model):
    name = models.CharField(max_length=80)

    class Meta:
        db_table = 'clients'
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def __str__(self):
        return self.name

    @classmethod
    def get_clients(self, request):
        from profiles.models import Profile

        if request.user.is_superuser:
            clients = Client.objects.all()
        else:
            auth_user = Profile.objects.get(auth=request.user.id)
            clients = Client.objects.filter(pk=auth_user.client_id)

        clients = list(clients.values())
        all_field = request.GET.get('all')

        if all_field:
            clients.insert(0, {'id': 0, 'name': all_field})

        return clients
