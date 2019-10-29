const { spawn, spawnSync } = require('child_process');
const { workerData, parentPort } = require('worker_threads')
const zlib = require('zlib');
const conn = require('../database/connect.js')();


class SNMP {
    constructor(conn) {
        this.rows = 0;
        this.device_id = null;
    }

    listOfListToDict(a) {
        let d = {};
        for (let i = 0; i < a.length; i++) {
            d[a[i][1]] = a[i][0]
        }
        return d
    }

    translate(OID){
        const ls = spawnSync('snmptranslate', [OID, '-Td', '-Of']);

        let stdout = ls.stdout.toString().split('\n');
        let info = {"DESCRIPTION": ""};
        let result = [];

        for(let r=0;r<stdout.length;r++){
            let l = stdout[r].trim();

            if (l.startsWith('-- FROM')) {
                info['MIB'] = l.split('-- FROM')[1].trim()
            }

            if (l.startsWith('SYNTAX')) {
                info['SYNTAX'] = l.split('SYNTAX')[1].trim();
                if (info['SYNTAX'].startsWith('INTEGER')) {
                    if(info['SYNTAX'].indexOf("{")>-1){
                        let syntax = info['SYNTAX'].replace('{', '|').replace('}', '|').split('|');
                        if (syntax.length == 3){
                            syntax = syntax[1].split(', ');
                            info['SYNTAX_2'] = this.listOfListToDict(syntax.map(x => (x.replace('(', '|').replace(')', '').split('|'))))
                        }
                    }
                }
            }

            if (info['DESCRIPTION'].endsWith('__')) {
                info['DESCRIPTION'] += l;
                if (! l.endsWith('"')){
                    info['DESCRIPTION'] += '__';
                }
            }

            if (l.startsWith('DESCRIPTION')) {
                info['DESCRIPTION'] = l.split('DESCRIPTION')[1].trim();
                if (!l.endsWith('"')) {
                    info['DESCRIPTION'] += '__';
                }
            }

            result.push(l);

        }

        if (result.length > 0) {
            let name = result[0].split(": ");
            if (name.length == 1) {
                info["name"] = name[0];
                info["DESCRIPTION"] = info["DESCRIPTION"].replace('__', ' ').trim('"');
            }
        }

        return info;
    }

    get_node(row) {
        let node = null;
        row = row.trim();

        if (!row) {
            return null;
        }

        let equalPos = row.indexOf('=');
        if (equalPos > -1) {
            node = {
                "addr": null,
                "value_type": null,
                "value": null,
                "mib_name": null,
                "mib_syntax": null,
                "mib_value": null,
                "mib_node_name": null,
                "mib_node_desc": null
            }
            
            node["addr"] = row.substring(0,equalPos - 1);
            if (!node["addr"]) {
                return null;
            }
            
            let description = row.substring(equalPos + 2);
            if (description.startsWith("No more variables left")) {
                return null;
            }
            
            let colonPos = description.indexOf(':');
            if (colonPos > -1) {
                node["value_type"] = description.substring(0, colonPos);
                node["value"] = description.substring(colonPos + 2);
            }else {
                node["value_type"] = '';
                node["value"] = description;
            }
            
            if (node["value_type"] == "STRING") {
                node["value"] = node["value"].trim('"');
            }
            //if (node["value_type"] == "Hex-STRING") {
            //  node["value"] = bytearray.fromhex(node["value"].replace(' ', '')).decode().replace('\x00', ' ');
            //}
            
            let info = this.translate(node["addr"]);
            if ('SYNTAX_2' in info) {
                node["mib_value"] = info['SYNTAX_2'][node["value"]] || node["value"];
            }
            
            node["mib_node_desc"] = info['DESCRIPTION'] || null;
            node["mib_name"] = info['MIB'] || null;
            node["mib_syntax"] = info['SYNTAX'] || null;
            let name = info['name'] || null;
            node["mib_node_name"] = (name && node["mib_name"]) ? name.replace(node["mib_name"] + "::", "") : null;
        }
        
        return node;
    }

    async insert_snmp_data(row, device_id){
        let node = this.get_node(row);
        if (node) {
            return await conn.promise().execute(`
                INSERT INTO snmp_device
                    (
                        updated,
                        device_id,addr,value_type,value,
                        mib_name,mib_syntax,mib_value,mib_node_name,mib_node_desc
                    )
                VALUES
                    (
                        @date,
                        ?,?,?,?,
                        ?,?,?,?,?
                    )
                `, [
                    device_id, node["addr"], node["value_type"], node["value"],
                    node["mib_name"], node["mib_syntax"], node["mib_value"], node["mib_node_name"], node["mib_node_desc"]
                ]);
        }
        
        return;
    }

    load_file(message, device_id) {
        conn.execute('select now() into @date');
        conn.execute('DELETE FROM snmp_device WHERE device_id=?', [device_id],(err)=>{
            if(err){
                throw new Error(err);
                return;
            }
            
            message.split('\n').forEach(row => {
                if (row && row.indexOf("Error in packet.") == -1){
                    this.insert_snmp_data(row, device_id);
                }
            });
            conn.end()
        })
    }

}


let action = workerData.action;
let device_name = workerData.device_name;
let buffer = workerData.buffer;
let message = zlib.unzipSync(buffer).toString();

if (! device_name){
    throw new Error('device not found')
}
if (! message){
    throw new Error('message is empty')
}

conn.execute(
    'SELECT id FROM devices WHERE name = ?', [device_name], (err, rows, fields) => {
        if (err){
            throw new Error(err)
            return;
        }

        if (rows.length > 0){
            let device_id = rows[0].id;
            let snmp_server = new SNMP();
    
            if (action === 'snmp_set_image') {
                snmp_server.load_file(message, device_id);
            }
        }else{
            throw new Error('device not found');
        }
});


