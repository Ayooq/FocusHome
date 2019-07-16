from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden
import Django.util as util
from Profiles.models import Profiles
from Devices.models import Devices
from Clients.models import Clients
from DeviceUnits.models import Units, Family, GPIOConfig, getPins as devicePins
from django.db import connection
import json
from django import forms

# Create your views here.


def index(request):
    if not request.user.has_perm('Devices.devices_list'):
        return HttpResponseForbidden()

    devices_list = Devices.objects.filter(id__gte=1)
    paginator = Paginator(devices_list, util.ITEM_PER_PAGE)
    page = request.GET.get('page')
    devices = paginator.get_page(page)

    return render(
        request, 'devices/index.html',
        {
            'page': {
                'title': util.get_app_name('Оборудование')
            },
            'devices': devices
        }
    )

def add(request):
    if not request.user.has_perm('Devices.devices_add'):
        return HttpResponseForbidden()

    if request.method == 'GET':
        device = Devices()

        cursor = connection.cursor()
        cursor.execute("""
            select
                duf.name as family__name,
                duf.title as family__title,
                duu.id as units__id,
                duu.name as units__name,
                duu.title as units__title,
                duu.is_pin,
                "" as gpio__format
            from {du_units_table} as duu
                inner join {du_family_table} as duf
                    on duf.id = duu.family_id
            where duu.is_custom=1
            order by duf.name, duu.name
            """.format(
                du_units_table=Units._meta.db_table,
                du_family_table=Family._meta.db_table,
            )
        )
        units = util.dictfetchall(cursor)
        cursor.close()

        return render(
            request, 'devices/edit.html',
            {
                'page': {
                    'title': util.get_app_name('Оборудование. Добавить')
                },
                'device': device,
                'clients': Clients.objects.all(),
                'units': units if units is not None else [],
                'pins': devicePins(),
                'errors': {}
            }
        )

    if request.method == 'POST':
        device = Devices()

        device.name = request.POST.get('name', "")
        device.address = request.POST.get('address', "")
        device.comment = request.POST.get('comment', "")
        device.uid = 0

        if request.user.is_superuser == 1:
            device.client_id = int(request.POST.get('client_id', 0))
        else:
            req_user = Profiles.objects.get(auth_id=request.user.id)
            device.client_id = req_user.client_id

        device.save()
        device.uid = "FP-{}".format(device.id)
        device.save()

        for unit in Units.objects.all():
            gpioDevice = GPIOConfig.objects.filter(
                 device_id=device.id,
                 unit_id=unit.id
            )

            if len(gpioDevice) == 0:
                gpioDevice = GPIOConfig()
            else:
                gpioDevice = gpioDevice[0]

            pinNumber = util.toInt(request.POST.get("client_pin_" + str(unit.id), -1))
            pinNumber = pinNumber if pinNumber in devicePins() else -1

            unitFormat = request.POST.get("client_unit_" + str(unit.id), "")
            if unitFormat != "":
                err = Devices.unitValidate(unitFormat)
                if err != 1:
                    # if not unitFormat in errors:
                    #     errors[unitFormat] = []
                    # errors[unitFormat].append(err)
                    unitFormat = ""

            gpioDevice.device_id=device.id
            gpioDevice.unit_id=unit.id
            gpioDevice.pin=pinNumber
            gpioDevice.format=unitFormat if unitFormat else None

            gpioDevice.save()

        # сформировать yaml и отправить
        GPIOConfig.create_yaml()

        return redirect('/devices/edit/'+str(device.id))


def edit(request, id):
    if not request.user.has_perm('Devices.devices_show'):
        return HttpResponseForbidden()

    errors = {}
    device = Devices.objects.get(id=id)

    if request.method == 'POST':
        if not request.user.has_perm('Devices.devices_edit'):
            return HttpResponseForbidden()

        device.name = request.POST.get('name', "")
        device.address = request.POST.get('address', "")
        device.comment = request.POST.get('comment', "")

        if request.user.is_superuser == 1:
            device.client_id = int(request.POST.get('client_id', 0))
        else:
            req_user = Profiles.objects.get(auth_id=request.user.id)
            device.client_id = req_user.client_id

        device.save()

        for unit in Units.objects.all():
            gpioDevice = GPIOConfig.objects.filter(
                 device_id=device.id,
                 unit_id=unit.id
            )

            if len(gpioDevice) == 0:
                gpioDevice = GPIOConfig()
            else:
                gpioDevice = gpioDevice[0]

            pinNumber = util.toInt(request.POST.get("client_pin_" + str(unit.id), -1))
            pinNumber = pinNumber if pinNumber in devicePins() else -1

            unitFormat = request.POST.get("client_unit_" + str(unit.id), "")
            if unitFormat != "":
                err = Devices.unitValidate(unitFormat)
                if err != 1:
                    if not unitFormat in errors:
                        errors[unitFormat] = []
                    errors[unitFormat].append(err)
                    unitFormat = ""


            gpioDevice.device_id=device.id
            gpioDevice.unit_id=unit.id
            gpioDevice.pin=pinNumber
            gpioDevice.format=unitFormat if unitFormat else None

            gpioDevice.save()

        # сформировать yaml и отправить
        GPIOConfig.create_yaml()


    cursor = connection.cursor()
    cursor.execute("""
        select
            dt.id as id,
            dt.name as name,
            dt.address as address,
            dt.uid as uid,
            ct.id as client__id,
            ct.name as client__name,
            duf.name as family__name,
            duf.title as family__title,
            duu.id as units__id,
            duu.name as units__name,
            duu.title as units__title,
            duu.is_pin,
            dug.id as gpio__id,
            dug.pin as gpio__pin,
            ifnull(dug.format, "") as gpio__format
            #COALESCE(dug.format, duu.format, "") as gpio__format
        from {devices_table} as dt
            inner join {clients_table} as ct
                on ct.id = dt.client_id
            inner join {du_units_table} as duu
                on duu.is_custom=1
            inner join {du_family_table} as duf
                on duf.id = duu.family_id
            left join {du_gpio_units_table} as dug
                on dug.device_id = dt.id
                and dug.unit_id = duu.id
        where dt.id={device_id} and ct.id={client_id}
        order by dt.id, duf.name, duu.name
    """.format(
            client_id=device.client_id,
            device_id=device.id,
            devices_table=Devices._meta.db_table,
            clients_table=Clients._meta.db_table,
            du_units_table=Units._meta.db_table,
            du_family_table=Family._meta.db_table,
            du_gpio_units_table=GPIOConfig._meta.db_table,
        )
    )
    units = util.dictfetchall(cursor)
    cursor.close()

    return render(
        request, 'devices/edit.html',
        {
            'page': {
                'title': util.get_app_name('Оборудование. Редактировать')
            },
            'device': device,
            'clients': Clients.objects.all(),
            'units': units if units is not None else [],
            'pins': devicePins(),
            'errors': errors
        }
    )

