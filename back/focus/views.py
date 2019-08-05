from django.contrib.auth import authenticate
from django.contrib.auth import login as basic_login
from django.contrib.auth import logout as basic_logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from . import utils


def login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect('monitoring:index')

        return render(
            request, 'focus/auth.html',
            {
                'page': {
                    'title': utils.get_app_name('Вход в личный кабинет')
                }
            }
        )

    elif request.method == 'POST':
        user = authenticate(username=request.POST.get(
            'email', ''), password=request.POST.get('psw', ''))

        if not user or not user.is_active:
            return redirect('login')

        basic_login(request, user)

        return redirect('monitoring:index')


def logout(request):
    basic_logout(request)

    return redirect('monitoring:index')


@login_required(login_url='login')
def help(request):

    return render(
        request, 'focus/help.html', {
            'page': {
                'title': utils.get_app_name('Справка')
            },
        }
    )
