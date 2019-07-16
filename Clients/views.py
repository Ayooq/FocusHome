from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden, JsonResponse
import Django.util as util
from Clients.models import Clients
from Profiles.models import Profiles


def index(request):
    if not request.user.has_perm('Clients.clients_list'):
        return HttpResponseForbidden()

    clients_list = Clients.objects.all()
    paginator = Paginator(clients_list, util.ITEM_PER_PAGE)
    page = request.GET.get('page')
    clients = paginator.get_page(page)

    return render(
        request, 'clients/index.html',
        {
            'page': {
                'title': util.get_app_name('Клиенты')
            },
            'clients': clients
        }
    )


def add(request):
    if not request.user.has_perm('Clients.clients_add'):
        return HttpResponseForbidden()

    if request.method == 'GET':
        client = Clients()

        return render(
            request, 'clients/edit.html',
            {
                'page': {
                    'title': util.get_app_name('Клиенты. Добавить')
                },
                'client': client
            }
        )

    if request.method == 'POST':
        client = Clients()
        name = request.POST.get('name', "")
        if name == "":
            return redirect('/clients/add')

        client.name = name
        client.save()

        return redirect('/clients/edit/' + str(client.id))


def edit(request, id):
    if not request.user.has_perm('Clients.clients_show'):
        return HttpResponseForbidden()

    client = Clients.objects.get(id=id)

    if request.method == 'POST':
        if not request.user.has_perm('Clients.clients_edit'):
            return HttpResponseForbidden()

        name = request.POST.get('name', "")
        if name == "":
            return redirect('/clients/edit/' + str(client.id))

        client.name = name
        client.save()

    return render(
        request, 'clients/edit.html',
        {
            'page': {
                'title': util.get_app_name('Клиенты. Редактировать')
            },
            'client': client
        }
    )


def api(request):
    action = request.GET.get('action', None)

    # if action == 'list':
    #     return get_clients_list(request)

    return JsonResponse({'data':[]}, status=404)



