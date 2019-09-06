import Django.util as util
from django.db import connection
from Django.models import BaseModel


class Profile(BaseModel):
    __perms = None

    def get(self):

        if self.id:
            query = """
                SELECT
                      au.id as auth_id
                    , '' as auth_password
                    , au.email as auth_email
                    , au.first_name as profile_firstname
                    , au.last_name as profile_lastname
                    , concat_ws(' ', au.first_name, au.last_name) as profile_name
                    , au.phone as profile_phone
                    , au.client_id as client_id
                FROM auth_user as au
                WHERE au.id=%(user_id)s
            """
            self.cursor.execute(query, {
                "user_id": self.id
            })
            self.data = util.dictfetchone(self.cursor)
        else:
            self.data =  {
                "auth_id": 0,
                "auth_password": '',
                "auth_email": '',
                "profile_firstname": '',
                "profile_lastname": '',
                "profile_name": '',
                "profile_phone": '',
                "client_id": 0
            }

        return self.data


    def set_perms(self):
        if self.__perms:
            return None

        query = """
            SELECT
                ap.codename
            FROM auth_user_user_permissions as up
                inner join auth_permission as ap
                    on ap.id = up.permission_id
                inner join django_content_type as dct
                    on dct.id = ap.content_type_id
            WHERE up.user_id=%(user_id)s
        """
        self.cursor.execute(query, {
            "user_id": self.id
        })
        rows = self.cursor.fetchall()

        perms = set()
        for row in rows:
            perms.add(row[0])

        self.__perms = perms

        return None


    def has_perm(self, perm_name):
        self.set_perms()
        return perm_name in self.__perms


    @staticmethod
    def check_email(email, white_list=None):
        if not email:
            return False
        if type(white_list) == list:
            if email in white_list:
                return True

        cursor = connection.cursor()
        query = """
            SELECT
                  au.id
            FROM auth_user as au
            WHERE au.email=%(email)s
        """
        cursor.execute(query, {
            "email": email
        })

        rowcount = cursor.rowcount
        cursor.close()

        return rowcount == 0
