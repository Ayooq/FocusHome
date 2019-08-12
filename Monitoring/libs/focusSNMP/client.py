import subprocess
from multiprocessing import Pool
import os


class SNMP:
    DEBUG = False
    ERROR_LOG = subprocess.STDOUT  # or file path

    def __init__(self, **kwargs):
        self.community = kwargs.get('community', 'public')
        self.version = kwargs.get('version', '2c')
        self.host = kwargs.get('host', '127.0.0.1:161')
        self.flags = kwargs.get('flags', ['Oe','On'])

    def __getdata(self, method, OID, file=None):
        cmd = "{method} -c {c} -v {v} {host} {flags} {oid}".format(
            method=method,
            c=self.community,
            v=self.version,
            host=self.host,
            oid=OID,
            flags=' '.join(['-' + str(f) for f in self.flags])
        ).split(" ")

        p = subprocess.Popen(cmd,
                             stdout=subprocess.PIPE,
                             stderr=self.ERROR_LOG)
        # p.wait()

        if self.DEBUG:
            print("focusSNMP::client::SNMP__getdata.cmd", ' '.join(cmd))

        result = [""]
        if file:
            with open(file, 'a') as f:
                for line in p.stdout:
                    l = line.decode("utf-8").rstrip()
                    if l.startswith('.1'):
                        f.write("\n" + l)
                    else:
                        f.write(" " + l.replace("\t", " "))
        else:
            for line in p.stdout:
                l = line.decode("utf-8").rstrip()
                if l.startswith('.1'):
                    result.append(l)
                else:
                    result[-1] += " " + l.replace("\t", " ")

        if result[0] == "":
            result.pop(0)

        return result

    def walk(self, OID, file=None):
        return self.__getdata("snmpwalk", OID, file)

    def bulkwalk(self, OID, file=None):
        return self.__getdata("snmpbulkwalk", OID, file)

    def get(self, OID):
        result = self.__getdata("snmpget", OID)
        if len(result) == 1:
            return result[0]

        return result

    def bulkget(self, OIDS):
        result = []
        for oid in OIDS:
            result.append(self.get(oid))

        return result

    def getImage(self, OIDs, file):
        for oid in OIDs:
            self.bulkwalk(oid, file)

        return 1
