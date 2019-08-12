# SNMP клиент

## Client (малинка)

```python
import PATH_TO.focusSNMP.client as focus_snmp_client
import time


snmp = focus_snmp_client.SNMP(
    community='public',
    version='2c',
    host='192.168.3.246',   #'192.168.3.40'
    flags=['Oe','On']
)
# имя файла
filePath = 'device_image_' + time.strftime("%Y%m%d%H%M%S") + '.txt'
# узлы, которые необходимо перебрать
nodes = ['.1.3.6.1.2', '.1.3.6.1.4.1.191']

# перебираем все датчики и пишим в файл filePath
snmp.getImage(nodes, file=filePath)

# отправляем на сервер файл filePath
# ...
# ...
# ...

```

## Server
```python
import Monitoring.libs.focusSNMP.server as focus_snmp_server


def connector(autocommit=True):
    try:
        conn = mysql.connector.connect(host='89.223.27.69',
                                       database='focus',
                                       user='FocusCore',
                                       password='GG1Dn9qUIKAd53Lp',
                                       autocommit=autocommit)
        if conn.is_connected():
            return conn

    except:
        print('connect error')

    return None


snmp = focus_snmp_server.SNMP(connector=connector)
snmp.load_file(file='PATH_TO_FILE', device_id='DEVICE_ID')

conn.close()
```


