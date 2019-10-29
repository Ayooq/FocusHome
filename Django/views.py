from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
import Django.util as util
from django.contrib.auth.decorators import login_required
from Settings.models import Settings
from django.http import JsonResponse
from django.db import connection
import uuid


@login_required(login_url='log_in')
def react_view(request):
    return render(
        request, 'views/index.html',
        {
            'settings': Settings.get(code=('monitoring_update_interval',))
        }
    )


def log_in(request):
    if request.method == 'GET':
        if request.user.is_authenticated == True:
            return redirect('/monitoring/')

        return render(
            request, 'auth/login.html',
            {
                'page': {
                    'title': 'Вход в личный кабинет'
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

        cursor = connection.cursor()
        # add socket key
        query = """
            UPDATE auth_user
            SET 
                socket_key=%(socket_key)s
            WHERE id=%(user_id)s;
        """
        cursor.execute(query, {
            'user_id': user.id,
            'socket_key': str(uuid.uuid4())
        })

        cursor.close()

        return redirect('/monitoring/')


def log_out(request):
    logout(request)

    return redirect('/login')


@login_required(login_url='log_in')
def help(request):

    return render(
        request, 'help/index.html', {
            'page': {
                'title': 'Справка'
            },
        }
    )


def settings(request):
    return JsonResponse(Settings.all(request), status=200)
