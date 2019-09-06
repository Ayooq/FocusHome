from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
import Django.util as util
from django.db import connection
from django.http import JsonResponse
from Profiles.models import Profile


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        is_ajax = request.is_ajax()

        if path in ('/login','/login/', '', '/'):
            return None

        # проверка авторизации
        if not request.user.is_authenticated:
            if is_ajax:
                return JsonResponse({
                    'message': 'Для просмотра необходима авторизация'
                }, status=401)
            else:
                return redirect('/login')

        body = {}
        if request.method == 'POST':
            if util.is_json(request.body):
                body = util.toJson(request.body)
        if request.method == 'GET':
            body = request.GET

        cursor = connection.cursor()
        profile = Profile(request.user.id)

        query = """
            select
                 au.id
                ,au.phone
                ,au.client_id
                ,au.role_id
                ,ag.code as role_code
            from auth_user as au
                inner join auth_group as ag
                    on ag.id = au.role_id
            where au.id=%(auth_id)s
        """
        cursor.execute(query, {
            'auth_id': request.user.id
        })
        row = cursor.fetchone()
        if not row:
            if is_ajax:
                return JsonResponse({
                    'message': 'Для просмотра необходима авторизация'
                }, status=401)
            else:
                return redirect('/login')

        request.user.phone = row[1]
        request.user.client_id = row[2]
        request.user.role_id = row[3]
        request.user.role_code = row[4]

        # разрешение на работу с устройством
        device_id = util.toInt(body.get('device_id', 0))
        if device_id > 0:
            query = """
                select
                    d.id
                from devices as d
                where d.id=%(device_id)s
                """ + (" and d.client_id = %(client_id)s" if request.user.role_code == 'clients' else '') + """
            """
            cursor.execute(query, {
                'device_id': device_id,
                'client_id': request.user.client_id
            })

            if cursor.rowcount == 0:
                return JsonResponse({
                    'message': 'Оборудование не найдено или недостачно прав для его просмотра'
                }, status=404)

        # разрешение на работу с клиентом
        client_id = util.toInt(body.get('client_id', 0))
        if client_id > 0:
            query = """
                select
                    c.id
                from clients as c
                where c.id=%(client_id)s
                """ + (" and c.id = %(client_id)s" if request.user.role_code == 'clients' else '') + """
            """
            cursor.execute(query, {
                'client_id': request.user.client_id
            })

            if cursor.rowcount == 0:
                return JsonResponse({
                    'message': 'Клиент не найден или недостачно прав для его просмотра'
                }, status=404)

        # разрешение на работу с пользователем
        user_id = util.toInt(body.get('user_id', 0))
        if user_id > 0:
            query = """
                select
                    au.id
                from auth_user as au
                where au.id=%(user_id)s
                """ + (" and au.client_id = %(client_id)s" if request.user.role_code == 'clients' else '') + """
            """
            cursor.execute(query, {
                'user_id': user_id,
                'client_id': request.user.client_id
            })

            if cursor.rowcount == 0:
                return JsonResponse({
                    'message': 'Пользователь не найден или недостачно прав для его просмотра'
                }, status=404)

        # добавление профиля авторизованного пользователя
        request.profile = profile

        return None
