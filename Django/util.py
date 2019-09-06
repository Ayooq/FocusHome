import json
import re
from Django.settings import DATABASES
import mysql.connector

ITEM_PER_PAGE = 30



def MSSQLConnector(autocommit=True):
    try:
        conn = mysql.connector.connect(host=DATABASES["default"]["HOST"],
                                       database=DATABASES["default"]["NAME"],
                                       user=DATABASES["default"]["USER"],
                                       password=DATABASES["default"]["PASSWORD"],
                                       autocommit=autocommit)
        if conn.is_connected():
            return conn

    except:
        print('connect error')

    return None


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def dictfetchone(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]

    row = cursor.fetchone()
    if row is None:
        return None

    return {
        columns[index]: item
        for index, item in enumerate(row)
    }

def is_float(s):
    if s is None or s == '' or s == 'None':
        return True

    return True if re.match(r"^[\d\.]*$", s) else False


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False

    return True


def toJson(text):
    return json.loads(text)

def jsonToStr(jsonDict):
    return json.dumps(jsonDict, ensure_ascii=False)

def toInt(s):
    if s is None or s == '' or s == 'None':
        return 0
    if s == 'on':
        return 1
    if type(s) == str:
        if not s.isdigit():
            return 0

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


def is_date(s, format):
    return True if re.match(format, s) else False


def toDate(s, format):
    """преобразовать строку в дату (''=None, None=None)
    format - YYYYMMDD, DD-MM-YYYY, YYYYMM01 ..."""

    if s is None or s == '':
        return None

    if re.match(r"[\d]{2}.[\d]{2}.[\d]{4}", s):  # 01.01.2018
        d = format
        d = d.replace('YYYY', s[6:10])
        d = d.replace('MM', s[3:5])
        d = d.replace('DD', s[:2])
        return d
    if re.match(r"[\d]{2}.[\d]{4}", s):  # 01.2018
        d = format
        d = d.replace('YYYY', s[3:7])
        d = d.replace('MM', s[:2])
        if re.match(r"\D\D", format):
            d = d.replace('DD', '01')
        return d

    return None


# "10..25" => (10,25)
def strRangeToTuple(s, separate=".."):
    sl = s.split(separate)
    if len(sl) == 2:
        return (toFloat(sl[0]), toFloat(sl[1]))

    return (0.0, 0.0)
