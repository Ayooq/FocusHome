from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
import Django.util as util
from Clients.models import Clients
from django.contrib.auth.decorators import login_required


def log_in(request):
    if request.method == 'GET':
        if request.user.is_authenticated == True:
            return redirect('/monitoring/')

        return render(
            request, 'auth/login.html',
            {
                'page': {
                    'title': util.get_app_name('Вход в личный кабинет')
                }
            }
        )

    if request.method == 'POST':
        user = authenticate(username=request.POST.get('email',''), password=request.POST.get('psw',''))
        if user is None:
            return redirect('/login')
        if user.is_active == 0:
            return redirect('/login')

        login(request, user)

        return redirect('/monitoring/')

def log_out(request):
    logout(request)

    return redirect('/monitoring')


@login_required(login_url='log_in')
def help(request):

    return render(
        request, 'help/index.html', {
            'page': {
                'title': util.get_app_name('Справка')
            },
        }
    )

