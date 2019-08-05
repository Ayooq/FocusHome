import json
import re

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.template.context_processors import request

from clients.models import Client
from configuration.models import Configuration
from devices.models import Config, Device
from focus.mqtt import client
from profiles.models import Profile
from units.models import Unit

ITEM_PER_PAGE = 30

# APP_NAME = 'FOCUS'
APP_NAME = Configuration.objects.filter(code='app_name')[0].value


def get_app_name(title=''):
    return APP_NAME + ': ' + title


def get_pins_total_count():
    return range(1, 31)


def list_fetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries."""

    columns = [col[0] for col in cursor.description]
    return [
        dict(
            zip(columns, row)
        ) for row in cursor.fetchall()
    ]


def set_context(title, device, units, errors={}):
    return {
        'page': {
            'title': get_app_name(title),
        },
        'device': device,
        'clients': Client.objects.all(),
        'units': units,
        'pins': get_pins_total_count(),
        'errors': errors,
    }


def add_or_edit_device(request, device=None, errors={}):
    device = device if device else Device()
    device.name = request.POST.get('name')
    device.address = request.POST.get('address')
    device.comment = request.POST.get('comment')

    if request.user.is_superuser:
        device.client_id = int(request.POST.get('client_id', 4))
    else:
        auth_user = Profile.objects.get(auth=request.user.id)
        device.client_id = auth_user.client_id

    device.save()

    if not device.name:
        device.name = 'FP-{}'.format(device.id)
        device.save()

    for unit in Unit.objects.all():
        try:
            config = Config.objects.get(
                device=device.id,
                unit=unit.id,
            )
        except Config.DoesNotExist:
            config = Config()

        pin = request.POST.get(
            'pin_for_' + str(unit.id)
        )
        pin = None if None else to_int(pin)

        format_ = request.POST.get('unit_definition_for_' + str(unit.id))

        if format_:
            error = Device.validate(format_)

            if error and errors.get(format_):
                errors[format_].append(error)
            elif error:
                errors[format_] = [error]

            format_ = '' if error else format_

        config.device_id = device.id
        config.unit_id = unit.id
        config.pin = pin
        config.format = format_
        config.save()

    # Сформировать yaml и отправить посреднику.
    new_config = config.form_json(device.id)
    client.publish('FP-2/cnf/self', new_config, qos=2)

    return device


def add_or_edit_profile(request, user, pk=None):
    user.firstname = request.POST.get('firstname', '')
    user.lastname = request.POST.get('lastname', '')
    user.phone = request.POST.get('phone', '')

    if request.user.is_superuser:
        user.role_id = int(request.POST.get('role_id', 1))
        user.client_id = int(request.POST.get('client_id', 1))
    else:
        req_user = Profile.objects.get(auth=request.user.id)
        user.client_id = req_user.client

    if pk:
        auth = User.objects.get(pk=user.auth.id)
        psw = request.POST.get('psw', '')

        if psw:
            auth.set_password(psw)

        auth.email = request.POST.get('email', '')
        auth.save()

    else:
        auth = User.objects.create_user(
            request.POST.get('user', ''),
            request.POST.get('email', ''),
            request.POST.get('psw', '')
        )

        user.auth_id = auth.id
        user.save()

    profile = Profile.objects.get(pk=user.id)

    return profile


def to_int(s):
    if not s or s == 'None':
        return 0

    elif s == 'on':
        return 1

    s = str(s)
    s = s.replace(',', '.')
    s = s.split('.')[0]
    s = re.sub(r'[^\-\d\.e]', '', s)

    return int(s)


def to_float(s):
    if not s or s == 'None':
        return 0.0

    s = str(s)
    s = s.replace(',', '.')
    s = re.sub(r'[^\-\d\.e]', '', s)

    return float(s)


# '10..25' => (10,25)
def str_range_to_tuple(s, sep='..'):
    slug = s.split(sep)

    if len(slug) == 2:
        return (to_float(slug[0]), to_float(slug[1]))

    return (0.0, 0.0)
