from Settings.models import Settings
import json
import re

ITEM_PER_PAGE = 30

APP_NAME = Settings.objects.filter(code='app_name')[0].value

def get_app_name(title=""):
    return APP_NAME + ": " + title


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False

    return True


def toInt(s):
    if s is None or s == '' or s == 'None':
        return 0
    if s == 'on':
        return 1

    s = str(s)
    s = s.replace(',', '.')
    s = s.split('.')[0]
    s = re.sub(r"[^\d\.\-e]", "", s)

    return int(s)


def toFloat(s):
    if s is None or s == '' or s == 'None':
        return 0.0

    s = str(s)
    s = s.replace(',', '.')
    s = re.sub(r"[^\d\.\-e]", "", s)

    return float(s)


# "10..25" => (10,25)
def strRangeToTuple(s, separate=".."):
    sl = s.split(separate)
    if len(sl) == 2:
        return (toFloat(sl[0]), toFloat(sl[1]))

    return (0.0, 0.0)
