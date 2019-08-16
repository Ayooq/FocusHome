import json
from itertools import chain

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import F
from django.shortcuts import redirect, render

from clients.models import Client
from devices.models import Config, Device
from focus import utils
from profiles.models import Profile
from units.models import Family, Unit

errors = {}


@permission_required('devices.view_device')
def index(request):
    devices = Device.objects.filter(pk__gte=1).order_by('name')
    paginator = Paginator(devices, utils.ITEM_PER_PAGE)
    page = request.GET.get('page')
    devices = paginator.get_page(page)

    return render(
        request, 'devices/index.html',
        {
            'page': {
                'title': utils.get_app_name('Оборудование')
            },
            'devices': devices,
        },
    )


@permission_required('devices.add_device')
def add(request):
    if request.method == 'POST':
        utils.add_or_edit_device(request, errors=errors)

        return redirect('devices:index')

    units = Unit.objects \
        .select_related('family') \
        .exclude(name='self') \
        .values(
            'id', 'is_gpio',
            'title', 'family__title',
        )

    return render(
        request, 'devices/edit.html',
        utils.set_context(
            'Добавить оборудование',
            Device(), units, errors,
        ),
    )


@permission_required('devices.change_device')
def edit(request, pk):
    device = Device.objects.get(pk=pk)

    if request.method == 'POST':
        device = utils.add_or_edit_device(request, device, errors)

    units = Config.objects \
        .select_related('unit') \
        .filter(device=pk) \
        .exclude(unit=1) \
        .values(
            'pin',
            family_title=F('unit__family__title'),
            title=F('unit__title'),
            name=F('unit__name'),
            is_gpio=F('unit__is_gpio'),
        )

    return render(
        request, 'devices/edit.html',
        utils.set_context(
            'Редактировать оборудование',
            device, units, errors,
        ),
    )


@permission_required('devices.delete_device')
def delete(request, pk):
    Device.objects.get(pk=pk).delete()

    return render(
        request, 'devices/index.html',
        {
            'page': {
                'title': utils.get_app_name('Оборудование')
            },
            'devices': Device.objects.all(),
        },
    )
