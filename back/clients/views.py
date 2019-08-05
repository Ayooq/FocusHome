from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import redirect, render

from focus import utils

from .models import Client


@permission_required('clients.view_client')
def index(request):
    clients = Client.objects.all().order_by('id')
    paginator = Paginator(clients, utils.ITEM_PER_PAGE)
    page = request.GET.get('page')
    clients = paginator.get_page(page)

    return render(
        request, 'clients/index.html',
        {
            'page': {
                'title': utils.get_app_name('Клиенты')
            },
            'clients': clients
        }
    )


@permission_required('clients.add_client')
def add(request):
    if request.method == 'GET':
        return render(
            request, 'clients/edit.html',
            {
                'page': {
                    'title': utils.get_app_name('Добавить клиента')
                },
                'client': Client()
            }
        )

    elif request.method == 'POST':
        client = Client()
        name = request.POST.get('name')

        if not name:
            return redirect('clients:add')

        client.name = name
        client.save()

        return redirect('clients:edit', client.id)


@permission_required('clients.change_client')
def edit(request, pk):
    client = Client.objects.get(pk=pk)

    if request.method == 'POST':
        name = request.POST.get('name')

        if not name:
            return redirect('clients:edit', client.id)

        client.name = name
        client.save()

    return render(
        request, 'clients/edit.html',
        {
            'page': {
                'title': utils.get_app_name('Редактировать клиента')
            },
            'client': client
        }
    )


@permission_required('clients.view_client')
def api(request):
    action = request.GET.get('action')

    if action == 'list':
        return Client.get_clients_list(request)

    return JsonResponse({'data': []}, status=404)
