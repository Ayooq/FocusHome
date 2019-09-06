from django.http import JsonResponse
import Django.util as util
from Clients.models import Client
from django.db import connection, transaction


def index(request):
    if not request.profile.has_perm('app.clients.index'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    client_name = request.GET.get('name', None)

    cursor = connection.cursor()
    query = """
        SELECT
              c.id as client_id
            , c.name as client_name
        FROM clients as c
        where 1=1
            """ + (" and c.name like %(client_name)s" if client_name else '') + """
    """
    cursor.execute(query, {
        "client_name": '%' + client_name + '%',
    })

    clients = util.dictfetchall(cursor)

    return JsonResponse({
        "title": 'Клиенты',
        "data": clients,
    }, status=200)


def edit(request):
    if not request.profile.has_perm('app.clients.show'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    client_id = request.GET.get('client_id', None)
    client = Client(id=client_id)

    return JsonResponse({
        "title": 'Клиенты. '+client.client_name,
        "client": client.to_dict()
    }, status=200)


def update(request):
    if not request.profile.has_perm('app.clients.update'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    if request.method == 'POST':
        body = request.body
        post = util.toJson(body)

        client_id = post.get('client_id', 0)

        transaction.set_autocommit(False)
        cursor = connection.cursor()

        client_data = post.get('client', None)
        if type(client_data) != dict:
            transaction.rollback()
            cursor.close()
            return JsonResponse({
                'message': 'неверный формат данных'
            }, status=400)

        client_name = str(client_data.get('client_name', '')).strip()
        if client_name == '':
            return JsonResponse({
                'message': 'Поле "Название" не заполнено'
            }, status=400)

        query = """
            UPDATE clients
            SET name=%(client_name)s
            WHERE id=%(client_id)s;
        """
        cursor.execute(query, {
            'client_id': client_id,
            'client_name': client_name
        })

        transaction.commit()
        cursor.close()

        return JsonResponse({
            'message': 'update'
        }, status=200)

    return JsonResponse({
        'message': 'метод не найден'
    }, status=404)


def create(request):
    if not request.profile.has_perm('app.clients.create'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    if request.method == 'GET':
        return __create_get(request)
    if request.method == 'POST':
        return __create_post(request)

    return JsonResponse({
        'message': 'метод не найден'
    }, status=404)


def __create_get(request):
    client = Client()

    return JsonResponse({
        "title": 'Клиенты. Создать нового',
        "client": client.to_dict()
    }, status=200)


def __create_post(request):
    body = request.body
    post = util.toJson(body)

    transaction.set_autocommit(False)
    cursor = connection.cursor()

    client_data = post.get('client', None)
    if type(client_data) != dict:
        transaction.rollback()
        cursor.close()
        return JsonResponse({
            'message': 'неверный формат данных'
        }, status=400)

    client_name = str(client_data.get('client_name', '')).strip()
    if client_name == '':
        return JsonResponse({
            'message': 'Поле "Название" не заполнено'
        }, status=400)

    # проверка на дубликат
    query = """
        select c.id
        from clients as c
        where c.name = %(client_name)s
    """
    cursor.execute(query, {
        'client_name': client_name
    })
    if cursor.rowcount:
        return JsonResponse({
            'message': 'Клиент с таким названием уже существует'
        }, status=400)

    query = """
        INSERT INTO clients
        (name)
        VALUES(%(client_name)s);
    """
    cursor.execute(query, {
        'client_name': client_name
    })

    query = """
        SELECT last_insert_id()
    """
    cursor.execute(query)
    row = cursor.fetchone()
    client_id = row[0]


    transaction.commit()
    cursor.close()

    return JsonResponse({
        'message': 'create',
        'client_id': client_id
    }, status=200)




