from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group, Permission, User
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from clients.models import Client
from devices.models import Device
from focus import utils
from profiles.models import Profile
from roles.models import Role


@permission_required('profiles.view_profile')
def index(request):
    profiles = Profile.objects.all().order_by('id')
    paginator = Paginator(profiles, utils.ITEM_PER_PAGE)
    page = request.GET.get('page')
    profiles = paginator.get_page(page)

    return render(
        request, 'profiles/index.html',
        {
            'page': {
                'title': utils.get_app_name('Пользователи')
            },
            'profiles': profiles,
        }
    )


@permission_required('profiles.add_profile')
def add(request):
    if request.method == 'GET':
        profile = Profile()

        return render(
            request, 'profiles/edit.html',
            {
                'page': {
                    'title': utils.get_app_name(
                        'Добавить новый профиль пользователя',
                    ),
                },
                'profile': profile,
                'roles': Role.objects.all(),
                'clients': Client.objects.all(),
            },
        )

    elif request.method == 'POST':
        profile = Profile()
        profile = utils.add_or_edit_profile(request, profile)

        return redirect('profiles:edit', pk=profile.id)


@permission_required('profiles.change_profile')
def edit(request, pk):
    profile = Profile.objects.get(pk=pk)

    if request.method == 'POST':
        profile = utils.add_or_edit_profile(request, profile, pk)

    return render(
        request, 'profiles/edit.html',
        {
            'page': {
                'title': utils.get_app_name(
                    'Редактировать профиль пользователя',
                ),
            },
            'profile': profile,
            'roles': Group.objects.all(),
            'clients': Client.objects.all()
        }
    )


@permission_required('profiles.change_profile')
def permit(request, pk):
    profile = Profile.objects.get(pk=pk)
    auth_user = User.objects.get(pk=profile.auth_id)

    perms_list = []
    perms_group = Group.objects.filter(pk=profile.role_id).order_by('name')

    if perms_group:
        perms_list = perms_group[0].permissions.all()

    if request.method == 'POST':
        for p in perms_list:
            if 'perm_' + str(p.id) in request.POST:
                auth.user_permissions.add(p.id)

    elif request.method == 'DELETE':
        for p in perms_list:
            if 'perm_' + str(p.id) in request.DELETE:
                auth.user_permissions.remove(p.id)

    profile_permissions = auth_user.user_permissions.values_list(
        'id', flat=True)

    return render(
        request, 'profiles/permit.html',
        {
            'page': {
                'title': utils.get_app_name('Права пользователей'),
            },
            'profile': profile,
            'profile_permissions': profile_permissions,
            'permissions_list': perms_list,
        }
    )
