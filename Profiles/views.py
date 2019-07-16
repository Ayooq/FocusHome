from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
import Django.util as util
from django.contrib.auth.models import User, Group, Permission
from django.http import HttpResponseForbidden
from Profiles.models import Profiles
from Devices.models import Devices
from Clients.models import Clients
from Roles.models import Roles


# Create your views here.


def index(request):
    if not request.user.has_perm('Profiles.users_list'):
        return HttpResponseForbidden()

    users_list = Profiles.objects.all()
    paginator = Paginator(users_list, util.ITEM_PER_PAGE)
    page = request.GET.get('page')
    users = paginator.get_page(page)

    return render(
        request, 'users/index.html',
        {
            'page': {
                'title': util.get_app_name('Пользователи')
            },
            'users': users
        }
    )


def add(request):
    if not request.user.has_perm('Profiles.users_add'):
        return HttpResponseForbidden()

    if request.method == 'GET':
        user = Profiles()

        return render(
            request, 'users/edit.html',
            {
                'page': {
                    'title': util.get_app_name('Пользователи. Добавить')
                },
                'user': user,
                'roles': Roles.objects.all(),
                'clients': Clients.objects.all()
            }
        )

    if request.method == 'POST':
        user = Profiles()

        user.lastname = request.POST.get('lastname', "")
        user.firstname = request.POST.get('firstname', "")
        user.phone = request.POST.get('phone', "")

        if request.user.is_superuser == 1:
            user.role_id = int(request.POST.get('role_id', 0))
            user.client_id = int(request.POST.get('client_id', 0))
        else:
            req_user = Profiles.objects.get(auth_id=request.user.id)
            # user.role_id = set default value
            user.client_id = req_user.client_id


        auth = User.objects.create_user(request.POST.get('email', ""), request.POST.get('email', ""), request.POST.get('psw', ""))

        user.auth_id = auth.id

        user.save()

        user = Profiles.objects.get(pk=user.id)

        return redirect('/users/edit/' + str(user.id))


def edit(request, id):
    if not request.user.has_perm('Profiles.users_show'):
        return HttpResponseForbidden()

    user = Profiles.objects.get(pk=id)

    if request.method == 'POST':
        if not request.user.has_perm('Profiles.users_edit'):
            return HttpResponseForbidden()

        user.lastname = request.POST.get('lastname', "")
        user.firstname = request.POST.get('firstname', "")
        user.phone = request.POST.get('phone', "")

        if request.user.is_superuser == 1:
            user.role_id = int(request.POST.get('role_id', 0))
            user.client_id = int(request.POST.get('client_id', 0))
        else:
            pass

        user.save()

        auth = User.objects.get(pk=user.auth.id)
        auth.email = request.POST.get('email', "")

        psw = request.POST.get('psw', "")
        if psw:
            auth.set_password(psw)

        auth.save()

        user = Profiles.objects.get(pk=id)

    return render(
        request, 'users/edit.html',
        {
            'page': {
                'title': util.get_app_name('Пользователи. Редактировать')
            },
            'user': user,
            'roles': Group.objects.all(),
            'clients': Clients.objects.all()
        }
    )


def perm(request, id):
    if not request.user.has_perm('Profiles.users_perm'):
        return HttpResponseForbidden()

    user = Profiles.objects.get(pk=id)
    auth = User.objects.get(pk=user.auth_id)

    perms_list = []
    perms_group = Group.objects.filter(id=user.role_id).order_by('name')
    if perms_group:
        perms_list = perms_group[0].permissions.all()

    if request.method == 'POST':
        for p in perms_list:
            if 'perm_'+str(p.id) in request.POST:
                auth.user_permissions.add(p.id)
            else:
                auth.user_permissions.remove(p.id)

    user_perm = list(auth.user_permissions.values_list('id', flat=True))

    return render(
        request, 'users/perm.html',
        {
            'page': {
                'title': util.get_app_name('Пользователи. Права')
            },
            'user': user,
            'user_perm': user_perm,
            'perms_list': perms_list
        }
    )
