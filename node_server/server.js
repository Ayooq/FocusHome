var mqtt = require('mqtt')
var app = require('express')();
//var http = require('http').Server(app);
var bodyParser = require("body-parser");
let mysql = require('mysql2');
const { Worker } = require("worker_threads");
const path = require("path");
const yaml = require('js-yaml');
const fs   = require('fs');
const config = yaml.safeLoad(fs.readFileSync(path.join(__dirname, "../config.yaml"), 'utf8'));

const debug = config.APP.debug;

if(config.APP.SSL === true){
    const cert_path = "/etc/letsencrypt/live/focus-pro.space/";
    var options = {
      key: fs.readFileSync(cert_path + 'privkey.pem'),
      cert: fs.readFileSync(cert_path + 'cert.pem')
    };
    var http = require('https').Server(options, app);
  }else{
    var http = require('http').Server(app);
  }


var mysql_pool  = mysql.createPool({
    connectionLimit : config.MYSQl.connectionLimit,
    host            : config.MYSQl.host,
    user            : config.MYSQl.user,
    password        : config.MYSQl.password,
    database        : config.MYSQl.database
});
var mqtt_client = mqtt.connect({
    host            : config.MQTT.host, 
    port            : config.MQTT.port, 
    clientId        : config.MQTT.clientId
});
const MONITORING_KEY = config.MONITORING.key;


function isJson(text) {
    return /^[\],:{}\s]*$/.test(text
        .replace(/\\["\\\/bfnrtu]/g, '@')
        .replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, ']')
        .replace(/(?:^|:|,)(?:\s*\[)+/g, '')
    );
}

mqtt_client.on('connect', function () {
    mqtt_client.subscribe('+/report/+', {'qos': 2}, function (err) {})
    mqtt_client.subscribe('+/snmp/+', {'qos': 2}, function (err) {})
})

mqtt_client.on('message', function (topic, message) {
    let topic_path = topic.split('/');
    let topic_path_len = topic_path.length;

    if (topic_path_len == 3) {
        let topic_name = topic_path[1];
        if (topic_name === 'report') {
            let device_name = topic_path[0];
            let unit_name = topic_path[2];
            let msg = message.toString();
            let payload = null;
        
            if (isJson(msg)) {
                payload = JSON.parse(msg);
                payload_to_proc = [
                    device_name,
                    unit_name,
                    payload[0],
                    payload[1],
                    payload[2]
                ]
        
                mysql_pool.execute('call broker_report_add(?,?,?,?,?)', payload_to_proc, function (error, results, fields){
                    if (results.length > 0){
                        if (results[0].length > 0) {
                            let row = results[0][0];
                            if ('device_id' in row && 'format' in row) {
                                io.to('device_inits_state::' + row.device_id).emit('device_inits_state', row.format);
                                io.to('devices_monitoring::' + row.client_id).emit('devices_monitoring', {
                                    'device_id': row.device_id,
                                    'unit_format': row.format
                                });
                            }
                        }
                    }
                })
            }
            
            if(debug){
                console.log('передача показаний датчиков', device_name, unit_name, payload);
            }
        }

        if (topic_name === 'snmp2') {
            let device_name = topic_path[0];
            let unit_name = topic_path[2];

            if (debug){
                console.log(topic_path);
            }

            let worker = new Worker(
                path.join(__dirname, "libs/snmp/snmp-worker.js"),
                {
                    'workerData': {
                        'action': 'snmp_set_image',
                        'device_name': device_name,
                        'buffer': message
                    }
                }
            );

            // worker.on("message", (msg) => console.log(msg));
            // worker.on("error", (error) => console.error("error", error));
            worker.on("exit", (code) => {
                if(debug){
                    console.log('worker-end');
                }
            });
        };
    }
})


app.use(bodyParser.urlencoded({extended: false}));
// проверка ключа
app.use('*', function (req, res, next) {
    if (req.body.monitoring_key != MONITORING_KEY) {
        res.statusCode = 404;
        return 0;
    }
    
    next();
});
// отправка команд на удаленное устройство
app.post('/send_message_to_device', function (req, res) {
    mqtt_client.publish(req.body.topic, req.body.payload, {'qos': 2});
    res.statusCode = 200;
    res.send();
})
// все остальное отсеиваем
app.get('*', function (req, res) {
    res.statusCode = 404;
    res.send();
});
app.post('*', function (req, res) {
    res.statusCode = 404;
    res.send();
});


/*
USER_ID = -1: django-socket-client
 */
var io = require('socket.io')(http);
io.set('transports', ['websocket']);
io.use(function (socket, next) {
    let socket_key = socket.handshake.query.socket || socket.handshake.headers.socket || null;
    let user_id = socket.handshake.query.user || socket.handshake.headers.user || null;
    
    if (socket_key && user_id){
        mysql_pool.execute('select id from auth_user where socket_key=? and id=?', [socket_key, user_id], function (error, results, fields){
            if (!error) {
                if (results.length > 0) {
                    socket.user_id = results[0].id
                    return next();
                }
            }
        });
    }
    return false;
});

// комнаты
// device_inits_state::DEVICE_ID - информация от датчиков по конкретному устройству
// devices_monitoring::CLIENT_ID - информация от датчиков всех устройств клиента

io.sockets.on('connection', function (socket) {
    if (debug){
        console.log('ws connected, user=', socket.user_id);
    }
    
    // пересылка django - mosquito
    // if (socket.user_id == -1) {
    //     socket.on('send_message_to_device', function (msg) {
    //         // проверяем права на данное сообщение
    //         if (msg.monitoring_key === MONITORING_KEY) {
    //             mqtt_client.publish(msg.topic, msg.payload, {'qos': 2});
    //         }
    //     });
    //    
    // }
    
    // подписка на информацию от датчиков устройства
    socket.on('subscribe:device_inits_state', function (msg) {
        // проверяем может ли пользователь работать с этим устройством, если да, то добавляем в список для рассылки
        mysql_pool.execute('select check_read_device(?,?) as device_id', [socket.user_id, msg.device_id], function (error, results, fields){
            if (!error) {
                if (results.length > 0) {
                    // добавляем в комнату
                    socket.join('device_inits_state::'+results[0].device_id)
                }
            }
        });
    });
    
    // отписка на информацию от датчиков устройства, если да, то удаляем из списка для рассылки
    socket.on('unsubscribe:device_inits_state', function (msg) {
        // проверяем может ли пользователь работать с этим устройством
        mysql_pool.execute('select check_read_device(?,?) as device_id', [socket.user_id, msg.device_id], function (error, results, fields){
            if (!error) {
                if (results.length > 0) {
                    // удаляем из комнаты
                    socket.leave('device_inits_state::'+results[0].device_id)
                }
            }
        });
    });

    // подписка на информацию от датчиков всех устройств
    socket.on('subscribe:devices_monitoring', function (msg) {
        // проверяем может ли пользователь работать с этим устройством, если да, то добавляем в список для рассылки
        mysql_pool.execute('select client_id from auth_user where id=?', [socket.user_id], function (error, results, fields){
            if (!error) {
                if (results.length > 0) {
                    // добавляем в комнату
                    socket.join('devices_monitoring::' + results[0].client_id);
                }
            }
        });
    });

    // отписка на информацию от датчиков всех устройств
    socket.on('unsubscribe:devices_monitoring', function (msg) {
        // проверяем может ли пользователь работать с этим устройством, если да, то добавляем в список для рассылки
        mysql_pool.execute('select client_id from auth_user where id=?', [socket.user_id], function (error, results, fields){
            if (!error) {
                if (results.length > 0) {
                    // удаляем из комнаты
                    socket.leave('devices_monitoring::' + results[0].client_id);
                }
            }
        });
    });

    socket.on('disconnect', function () {
        if (debug){
            console.log('ws disconnected, user=', socket.user_id);
        }
    });

});

http.listen(config['SOCKET-SERVER'].host.split("/")[2].split(":")[1], function () {
    if (debug){
        console.log('proxy server run');
    }
});
