import Django.util as util
from django.http import JsonResponse
from Profiles.models import Profile
from django.contrib.auth.hashers import make_password
from django.db import connection, transaction


def index(request):
    if not request.profile.has_perm('app.users.index'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    client_name = request.GET.get('client_name', '')
    user_name = request.GET.get('user_name', '')

    cursor = connection.cursor()
    query = """
        SELECT
              au.id as auth_id
            , concat(au.last_name, ' ', au.first_name) as profile_name
            , c.name as client_name
        FROM auth_user as au
            inner join clients as c
                on c.id = au.client_id
        where 1=1
            """ + (" and c.name like %(client_name)s" if client_name else '') + """
            """ + (" and concat(au.last_name, ' ', au.first_name) like %(user_name)s" if user_name else '') + """
            """ + (" and au.client_id = %(client_id)s" if request.user.role_code == 'clients' else '') + """
    """
    cursor.execute(query, {
        "client_name": '%' + client_name + '%',
        "user_name": '%' + user_name + '%',
        "client_id": request.user.client_id
    })

    users = util.dictfetchall(cursor)

    return JsonResponse({
        "title": 'Пользователи',
        "data": users,
    }, status=200)


def edit(request):
    if not request.profile.has_perm('app.users.show'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    user_id = request.GET.get('user_id', None)

    user = Profile(user_id)

    return JsonResponse({
        "title": 'Пользователи. ' + user.profile_name,
        "user": user.to_dict(),
        "is_client_change": False,
        "is_perm_change": request.profile.has_perm('app.users.perm')
    }, status=200)


def update(request):
    if not request.profile.has_perm('app.users.update'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    if request.method == 'POST':
        body = request.body
        post = util.toJson(body)

        user_id = post.get('user_id', 0)

        user_data = post.get('user', None)
        if type(user_data) != dict:
            return JsonResponse({
                'message': 'неверный формат данных'
            }, status=400)

        auth_password = user_data.get('auth_password', '')
        auth_email = str(user_data.get('auth_email', '')).strip()
        profile_firstname = str(user_data.get('profile_firstname', '')).strip()
        profile_lastname = str(user_data.get('profile_lastname', '')).strip()
        profile_phone = str(user_data.get('profile_phone', '')).strip()

        msg_error = None
        if not auth_email:
            msg_error = 'Заполните поле "Электронная почта"'
        if not Profile.check_email(auth_email, [request.profile.auth_email]):
            msg_error = 'На указанную электронную почту уже зарегистрирован другой пользователь'
        if not profile_firstname or not profile_lastname:
            msg_error = 'Заполните поле "ФИО"'

        if msg_error:
            return JsonResponse({
                'message': msg_error
            }, status=400)

        cursor = connection.cursor()

        query = """
            UPDATE auth_user
            SET 
                """ + ("password=%(auth_password)s," if auth_password else "") + """
                email=%(auth_email)s,
                username=%(auth_email)s,
                first_name=%(firstname)s,
                last_name=%(lastname)s,
                phone=%(phone)s
            WHERE id=%(user_id)s;
        """
        cursor.execute(query, {
            'user_id': user_id,
            'auth_email': auth_email,
            'auth_password': make_password(auth_password) if auth_password else None,
            'firstname': profile_firstname,
            'lastname': profile_lastname,
            'phone': profile_phone
        })

        cursor.close()

        return JsonResponse({
            'message': 'update'
        }, status=200)

    return JsonResponse({
        'message': 'метод не найден'
    }, status=404)


def create(request):
    if not request.profile.has_perm('app.users.create'):
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
    user = Profile()

    user.client_id = request.user.client_id

    return JsonResponse({
        "title": 'Пользователи. Добавить нового',
        "user": user.to_dict(),
        "is_client_change": request.user.role_code == 'management'
    }, status=200)


def __create_post(request):
    body = request.body
    post = util.toJson(body)

    user_data = post.get('user', None)
    if type(user_data) != dict:
        return JsonResponse({
            'message': 'неверный формат данных'
        }, status=400)

    auth_password = user_data.get('auth_password', '')
    auth_email = str(user_data.get('auth_email', '')).strip()
    profile_firstname = str(user_data.get('profile_firstname', '')).strip()
    profile_lastname = str(user_data.get('profile_lastname', '')).strip()
    profile_phone = str(user_data.get('profile_phone', '')).strip()
    client_id = util.toInt(user_data.get('client_id', 0))

    msg_error = None
    if not auth_email:
        msg_error = 'Заполните поле "Электронная почта"'
    if not Profile.check_email(auth_email):
        msg_error = 'На указанную электронную почту уже зарегистрирован другой пользователь'
    if not auth_password:
        msg_error = 'Заполните поле "Пароль"'
    if not profile_firstname or not profile_lastname:
        msg_error = 'Заполните поле "ФИО"'

    if msg_error:
        return JsonResponse({
            'message': msg_error
        }, status=400)

    cursor = connection.cursor()

    if client_id == 0:
        query = """
            SELECT
                au.client_id as client_id
            from auth_user as au
            where au.id = %(auth_id)s
        """
        cursor.execute(query, {
            'auth_id': request.user.id
        })
        row = cursor.fetchone()
        client_id = row[0]

    query = """
        INSERT INTO auth_user
        (
            password, email, username, is_superuser, is_staff, is_active, date_joined,
            first_name, last_name, phone, client_id, role_id
        )
        VALUES(
            %(auth_password)s, %(auth_email)s, %(auth_email)s, 0, 0, 1, now(),
            %(firstname)s, %(lastname)s, %(phone)s, %(client_id)s, %(role_id)s
        );
    """

    role_id = 2
    # если пользователя создает клиент
    if request.user.role_code == 'clients':
        role_id = 2
    # если пользователя создает сотрудник АТМ для своей организации
    elif request.user.role_code == 'management' and client_id == 4:
        role_id = 1

    cursor.execute(query, {
        'auth_email': auth_email,
        'auth_password': make_password(auth_password),
        'client_id': client_id,
        'firstname': profile_firstname,
        'lastname': profile_lastname,
        'phone': profile_phone,
        'role_id': role_id
    })

    query = """
        SELECT last_insert_id()
    """
    cursor.execute(query)
    row = cursor.fetchone()
    auth_id = row[0]

    cursor.close()

    return JsonResponse({
        'message': 'create',
        'user_id': auth_id
    }, status=200)


def perm(request):
    if not request.profile.has_perm('app.users.perm'):
        return JsonResponse({
            'message': 'Доступ запрещен'
        }, status=403)

    if request.method == 'GET':
        return __perm_get(request)
    if request.method == 'POST':
        return __perm_post(request)

    return JsonResponse({
        'message': 'метод не найден'
    }, status=404)


def __perm_get(request):
    user_id = request.GET.get('user_id', 0)
    user = Profile(user_id)

    perms = {}

    cursor = connection.cursor()

    group_codes = ["''"]
    if request.user.role_code == 'clients':
        group_codes = ["'clients'"]
    if request.user.role_code == 'management':
        group_codes = ["'management'","'clients'"]

    query = """
        SELECT
             ap.id
            ,dct.app_label
            ,ap.name
            ,(aup.permission_id=ap.id) as `check`
        from auth_group as ag
            inner join django_content_type as dct
                on dct.auth_group_id = ag.id
            inner join auth_permission as ap
                on ap.content_type_id = dct.id
            left join auth_user_user_permissions as aup
                on aup.permission_id = ap.id
                and aup.user_id = %(user_id)s
        where ag.code in (""" + (",".join(group_codes)) + """)
        order by dct.app_label, ap.name
    """
    cursor.execute(query, {
        'user_id': user.auth_id
    })
    rows = cursor.fetchall()
    for row in rows:
        if not row[1] in perms:
            perms[row[1]] = []
        perms[row[1]].append({
            'id': row[0],
            'group': row[1],
            'name': row[2],
            'check': row[3] == 1
        })


    return JsonResponse({
        'title': 'Права пользователя',
        'user': user.to_dict(),
        'perms': perms
    }, status=200)


def __perm_post(request):
    body = request.body
    post = util.toJson(body)
    user_id = post.get('user_id', None)
    profile = Profile(user_id)
    cursor = connection.cursor()

    perms = post.get('perms', None)
    if type(perms) != list:
        return JsonResponse({
            'message': 'неверный формат данных'
        }, status=400)

    perms = list(map(util.toInt, perms))
    perms = list(map(str, perms))

    if len(perms) > 0:
        group_codes = ["''"]
        if request.user.role_code == 'clients':
            group_codes = ["'clients'"]
        if request.user.role_code == 'management':
            group_codes = ["'management'","'clients'"]

        query = """
            SELECT
                 ap.id
            from auth_group as ag
                inner join django_content_type as dct
                    on dct.auth_group_id = ag.id
                inner join auth_permission as ap
                    on ap.content_type_id = dct.id
            where 
                ag.code in (""" + (",".join(group_codes)) + """)
                and ap.id in  (""" + (",".join(perms)) + """)
            order by dct.app_label, ap.name
        """
        cursor.execute(query, {})
        rows = cursor.fetchall()
        perms = []
        for row in rows:
            perms.append(str(row[0]))

    transaction.set_autocommit(False)
    # удаляем права, которые отменили
    if len(perms) > 0:
        query = """
            DELETE FROM auth_user_user_permissions
            WHERE user_id=%(user_id)s
                and permission_id not in (""" + (",".join(perms)) + """)
        """
        cursor.execute(query, {
            'user_id': profile.auth_id
        })
    else:
        query = """
            DELETE FROM auth_user_user_permissions
            WHERE user_id=%(user_id)s
        """
        cursor.execute(query, {
            'user_id': profile.auth_id
        })

    # добавляем новые права
    for perm in perms:
        query = """
            INSERT INTO auth_user_user_permissions
                (
                    `user_id`, `permission_id`
                )
            VALUES
                (
                    %(user_id)s, %(permission_id)s
                )
            ON DUPLICATE KEY UPDATE
                `user_id` = VALUES (`user_id`),
                `permission_id` = VALUES (`permission_id`)
        """
        cursor.execute(query, {
            'user_id': profile.auth_id,
            'permission_id': perm
        })

    transaction.commit()

    return JsonResponse({
        'message': 'update'
    }, status=200)

