from django.db import models
from django.db import connection
import Django.util as util


class Groups(models.Model):
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.name


class Types(models.Model):
    type = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        primary_key=True
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.name


class Settings(models.Model):
    group = models.ForeignKey(
        Groups,
        on_delete=models.CASCADE,
        default=None
    )

    code = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        unique=True
    )
    name = models.CharField(
        max_length=255,
        blank=False,
        null=False
    )
    datatype = models.ForeignKey(
        Types,
        on_delete=models.CASCADE,
        default=None
    )
    value = models.TextField(
        blank=False,
        null=False
    )
    comment = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        default=None
    )

    class Meta:
        db_table = 'config'

    def __str__(self):
        return "{} ({}=({}){})".format(self.name, self.code, self.type_id, self.value if len(self.value) < 20 else self.value[:20] + "...")

    @staticmethod
    def get(code=()):
        config = {}
        if len(code)>0:
            items = Settings.objects.filter(code__in=code).values('code','value','datatype_id')
            for item in items:
                config[item['code']] = item['value']

        return config

    @staticmethod
    def all(request):
        cursor = connection.cursor()
        query = """
            select
            *
            from config
        """
        cursor.execute(query, {})
        rows = util.dictfetchall(cursor)

        config_db = {}
        for row in rows:
            config_db[row['code']] = {
                'code': row['code'],
                'value': row['value'],
                'datatype_id': row['datatype_id']
            }
        app_name = config_db.pop('app_name', dict())

        query = """
            select
                 am.id
                ,am.parent
                ,am.title
                ,am.icon
                ,am.href
            from app_menu as am
            where 
                am.is_active = 1
                and 
                (
                    EXISTS (
                        select au.id
                        FROM auth_user as au
                            inner join auth_user_user_permissions as up
                                on up.user_id = au.id
                            inner join auth_permission as ap
                                on ap.id = up.permission_id
                        where au.id=%(user_id)s and ap.codename = am.perm
                    )
                    OR
                    am.perm is NULL
                )
        """
        cursor.execute(query, {
            'user_id': request.user.id
        })
        app_menu = util.dictfetchall(cursor)

        config = {
            'app': {
                'name': app_name.get('value', '')
            },
            'clients': [],
            'group': config_db,
            'menu': app_menu
        }

        if request.user.role_code == 'management':
            query = """
                select
                     c.id
                    ,c.name
                from clients as c
                order by c.name
            """
            cursor.execute(query, {})
            rows = cursor.fetchall()
            for row in rows:
                config['clients'].append({'id': row[0], 'name': row[1]})

        cursor.close()

        return config
