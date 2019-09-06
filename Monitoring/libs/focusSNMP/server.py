import subprocess
import os
import json
from multiprocessing import Pool, Process
import re


def is_float(s):
    if s is None or s == '' or s == 'None':
        return True

    return True if re.match(r"^[\d\.]*$", s) else False


def toFloat(s):
    if s is None or s == '' or s == 'None':
        return 0.0

    s = str(s)
    s = s.replace(',', '.')
    s = re.sub(r"[^\d\.\-e]", "", s)

    return float(s)


class SNMP:

    def __init__(self, connector=None):
        self.connector = connector

    @staticmethod
    def listOfListToDict(a):
        d = {}
        for i in a:
            d[i[1]] = i[0]

        return d

    @staticmethod
    def translate(OID):
        cmd = "snmptranslate {oid} {flags}".format(
            oid=OID,
            flags='-Td -Of'
        ).split(" ")

        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)

        result = []
        info = {"DESCRIPTION": ""}
        for line in p.stdout:
            l = line.decode("utf-8").strip()
            if l.startswith('-- FROM'):
                info['MIB'] = l.split('-- FROM')[1].strip()
            if l.startswith('SYNTAX'):
                info['SYNTAX'] = l.split('SYNTAX')[1].strip()
                if info['SYNTAX'].startswith('INTEGER'):
                    if info['SYNTAX'].find('{'):
                        syntax = info['SYNTAX'].replace('{', '|').replace('}', '|').split('|')
                        if len(syntax) == 3:
                            syntax = syntax[1].split(', ')
                            info['SYNTAX_2'] = SNMP.listOfListToDict(list(map(lambda x: x.replace('(', '|').replace(')', '').split('|'), syntax)))

            if info['DESCRIPTION'].endswith('__'):
                info['DESCRIPTION'] += l
                if not l.endswith('"'):
                    info['DESCRIPTION'] += '__'
            if l.startswith('DESCRIPTION'):
                info['DESCRIPTION'] = l.split('DESCRIPTION')[1].strip()
                if not l.endswith('"'):
                    info['DESCRIPTION'] += '__'

            result.append(l)

        if len(result) > 0:
            name = result[0].split(": ")
            if len(name) == 1:
                info["name"] = name[0]
                info["DESCRIPTION"] = info["DESCRIPTION"].replace('__', ' ').strip('"')

        return info

    @staticmethod
    def get_node(row):
        node = None
        row = row.strip()

        if not row:
            return None

        equalPos = row.find('=')
        if equalPos > -1:
            node = {
                "addr": None,
                "value_type": None,
                "value": None,
                "mib_name": None,
                "mib_syntax": None,
                "mib_value": None,
                "mib_node_name": None,
                "mib_node_desc": None
            }

            node["addr"] = row[:equalPos - 1]
            if not node["addr"]:
                return None

            description = row[equalPos + 2:]
            if description.startswith("No more variables left"):
                return None

            colonPos = description.find(':')
            if colonPos > -1:
                node["value_type"] = description[:colonPos]
                node["value"] = description[colonPos + 2:]
            else:
                node["value_type"] = ''
                node["value"] = description

            if node["value_type"] == "STRING":
                node["value"] = node["value"].strip('"')
            # if node["value_type"] == "Hex-STRING":
            #     node["value"] = bytearray.fromhex(node["value"].replace(' ', '')).decode().replace('\x00', ' ')

            info = SNMP.translate(node["addr"])
            if 'SYNTAX_2' in info:
                node["mib_value"] = info['SYNTAX_2'].get(node["value"], node["value"])

            node["mib_node_desc"] = info.get('DESCRIPTION', None)
            node["mib_name"] = info.get('MIB', None)
            node["mib_syntax"] = info.get('SYNTAX', None)
            name = info.get('name', None)
            node["mib_node_name"] = name.replace(node["mib_name"] + "::", "") if (name and node["mib_name"]) else None

        return node

    def insert_history(self, file, device_id):

        conn = self.connector()
        cursor = conn.cursor()

        result = []

        with open(file) as f:
            for row in f:
                node = self.get_node(row)

                cursor.callproc('snmp_value_add', (
                    device_id,
                    node["addr"],
                    node["value_type"],
                    node["value"],
                    node["mib_name"],
                    node["mib_syntax"],
                    node["mib_value"],
                    node["mib_node_name"],
                    node["mib_node_desc"],
                    1
                ))

                for rows in cursor.stored_results():
                    for row in rows.fetchall():
                        result.append(row)

        conn.close()

        return result


    def insert_value(self, file, device_id):
        conn = self.connector()
        cursor = conn.cursor()

        with open(file) as f:
            for row in f:
                node = self.get_node(row)

                cursor.callproc('snmp_value_add', (
                    device_id,
                    node["addr"],
                    node["value_type"],
                    node["value"],
                    node["mib_name"],
                    node["mib_syntax"],
                    node["mib_value"],
                    node["mib_node_name"],
                    node["mib_node_desc"],
                    0
                ))

        conn.close()

        return []

    @staticmethod
    def insert_snmp_data(connector, device_id, rows, index=0):
        conn = connector()
        cursor = conn.cursor()

        cursor.execute("select now() into @date")

        for row in rows:
            node = SNMP.get_node(row)
            if node is not None:
                cursor.execute("""
                    INSERT INTO snmp_device
                        (
                            updated,
                            device_id,addr,value_type,value,
                            mib_name,mib_syntax,mib_value,mib_node_name,mib_node_desc
                        )
                    VALUES
                        (
                            @date,
                            %s,%s,%s,%s,
                            %s,%s,%s,%s,%s
                        )
                """, (
                    device_id, node["addr"], node["value_type"], node["value"],
                    node["mib_name"], node["mib_syntax"], node["mib_value"], node["mib_node_name"], node["mib_node_desc"]
                ))

        conn.commit()
        conn.close()
        print("proc end: ", index)

    def load_file(self, file, device_id):
        row_index = 0

        conn = self.connector()
        cursor = conn.cursor()
        cursor.execute("select now() into @date")
        cursor.execute("DELETE FROM snmp_device WHERE device_id=%s", (device_id,))
        conn.close()

        procs = []

        with open(file) as f:
            rows = []
            for row in f:
                if row and row.find("Error in packet.") == -1:
                    rows.append(row)
                    if len(rows) % 100 == 0:
                        proc = Process(target=SNMP.insert_snmp_data, args=(self.connector, device_id, rows, len(procs)))
                        procs.append(proc)
                        proc.start()

                        rows = []

            proc = Process(target=SNMP.insert_snmp_data, args=(self.connector, device_id, rows))
            procs.append(proc)
            proc.start()

        for proc in procs:
            proc.join()

        return row_index

    def mib_reparse(self):
        conn = self.connector()
        cursor = conn.cursor()
        cursor.execute("select device_id, addr, value from snmp_device where mib_syntax is null")

        rows = cursor.fetchall()

        for row in rows:
            info = self.translate(row[1])

            if 'name' in info:
                if 'MIB' in info:
                    info['name'] = info['name'].replace(info['MIB'] + '::', '')

            if 'SYNTAX' in info:
                cursor.execute("""
                    UPDATE snmp_device
                    SET mib_name = %s
                    , mib_syntax = %s
                    , mib_node_name = %s
                    , mib_node_desc = %s
                    , mib_value = %s
                    WHERE device_id = %s and addr = %s;
                """, (
                    info.get('MIB', None)
                    , info.get('SYNTAX', None)
                    , info.get("name", None)
                    , info.get("DESCRIPTION", None)
                    , info['SYNTAX_2'].get(row[2], row[2]) if 'SYNTAX_2' in info else None
                    , row[0], row[1]
                ))

        print('mib_reparse')
        conn.close()

        return 1

    def get_tree(self, device_id):
        conn = self.connector()
        cursor = conn.cursor()
        cursor.execute("select device_id, addr, mib_node_name, value from snmp_device where device_id=%s", (device_id,))
        rows = cursor.fetchall()

        tree = {'mib': '', 'sensors': 0}
        for row in rows:
            addr = row[1][1:].split('.')[:-1]
            mib_addr = row[2][1:].split('.')[:-1]

            s = tree
            _addr = ['']
            _mib_addr = ''
            for index, a in enumerate(addr):
                _addr.append(a)
                if index < len(mib_addr):
                    _mib_addr = mib_addr[index]
                else:
                    _mib_addr = mib_addr[-1]
                address = '.'.join(_addr)
                mib_address = _mib_addr + (' ('+a+')' if _mib_addr != a else '')
                if mib_address not in s:
                    s[mib_address] = {'mib': address, 'sensors': 0}
                s = s[mib_address]
            s['sensors'] += 1

        # print(json.dumps(tree, indent=4))
        # tree = SNMP.dict_recursive(tree)

        # print(json.dumps(tree, indent=4))
        # f = open('log.json', 'w')
        # f.write(json.dumps(tree, indent=4))
        # f.close()
        conn.close()

        return tree

    @staticmethod
    def dict_recursive(_dict):
        keys_filter = lambda x: x not in ['sensors', 'mib']

        keys = list(filter(keys_filter, _dict.keys()))

        if len(keys) == 0:
            return _dict
        if len(keys) == 1:
            return SNMP.dict_recursive(_dict[keys[0]])

        for key in list(filter(keys_filter, _dict.keys())):
            _dict[key] = SNMP.dict_recursive(_dict[key])

        return _dict

    def get_table(self, device_id, addr):
        conn = self.connector()
        cursor = conn.cursor()
        cursor.execute("""select 
              addr
            , value_type
            , COALESCE(mib_value, value) as value
            , mib_node_name
            , mib_node_desc
        from snmp_device where device_id=%s and addr like %s""", (device_id, addr + '%'))
        rows = cursor.fetchall()

        tbl_data = {}
        for row in rows:
            tblCR = row[3].split('.')
            if len(tblCR) > 1:
                colName = tblCR[-2]
                rowName = tblCR[-1]

                if rowName not in tbl_data:
                    tbl_data[rowName] = {}
                if colName not in tbl_data[rowName]:
                    tbl_data[rowName][colName] = [row[0], None]

                tbl_data[rowName][colName][1] = row[2]

        data = []
        columns = []
        keys = list(tbl_data.keys())
        if len(keys) > 0:
            columns = list(tbl_data[keys[0]].keys())

            for k in keys:
                tbl_row = []
                for col in columns:
                    if col in tbl_data[k]:
                        tbl_row.append(tbl_data[k][col])
                    else:
                        tbl_row.append("None")
                data.append(tbl_row)

        conn.close()

        return columns, data
