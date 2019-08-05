import json

from django.contrib.auth.decorators import permission_required
from django.core.paginator import Paginator
from django.db import connection
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
    if request.method == 'GET':
        cursor = connection.cursor()
        cursor.execute('''
            SELECT
                uft.name AS family_name,
                uft.title AS family_title,
                ut.id, ut.name, ut.title, ut.is_gpio
            FROM {units_table} AS ut
                INNER JOIN {units_family_table} AS uft
                    ON uft.id = ut.family_id
            WHERE ut.is_custom = 1
            ORDER BY family_name, ut.name;
        '''.format(
            units_table=Unit._meta.db_table,
            units_family_table=Family._meta.db_table,
        ))

        units = utils.list_fetchall(cursor)
        cursor.close()

        return render(
            request, 'devices/edit.html',
            utils.set_context(
                'Добавить оборудование',
                Device(), units, errors,
            ),
        )

    elif request.method == 'POST':
        device = utils.add_or_edit_device(request, errors=errors)

        return redirect('devices:edit', pk=device.id)


@permission_required('devices.change_device')
def edit(request, pk):
    device = Device.objects.get(pk=pk)

    if request.method == 'POST':
        device = utils.add_or_edit_device(request, device, errors)

    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            dt.id AS device_id,
            dt.name AS device_name,
            dt.address AS device_address,
            ct.id AS client_id,
            ct.name AS client_name,
            uft.name AS family_name,
            uft.title AS family_title,
            ut.id, ut.name, ut.title, ut.is_gpio,
            dct.pin AS mounted_unit_pin,
            dct.format
        FROM {devices_table} AS dt
            INNER JOIN {clients_table} AS ct
                ON ct.id = dt.client_id
            INNER JOIN {units_table} AS ut
                ON ut.is_gpio = 1
            INNER JOIN {units_family_table} AS uft
                ON uft.id = ut.family_id
            LEFT JOIN {devices_config_table} AS dct
                ON dct.device_id = dt.id
                AND dct.unit_id = ut.id
        WHERE dt.id={device_id}
        ORDER BY device_id, family_name, name;
    '''.format(
        # client_id=device.client_id,
        clients_table=Client._meta.db_table,
        device_id=device.id,
        devices_table=Device._meta.db_table,
        devices_config_table=Config._meta.db_table,
        units_table=Unit._meta.db_table,
        units_family_table=Family._meta.db_table,
    ))

    units = utils.list_fetchall(cursor)
    cursor.close()

    return render(
        request, 'devices/edit.html',
        utils.set_context(
            'Редактировать оборудование',
            device, units, errors,
        ),
    )
