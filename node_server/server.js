var mqtt = require('mqtt')
var app = require('express')();
var http = require('http').Server(app);
var bodyParser = require("body-parser");
let mysql = require('mysql2');


app.use(bodyParser.urlencoded({extended: false}));
var mqtt_client = mqtt.connect({host: '89.223.27.69', port: 1883, clientId: 'node_dispatcher'});
var io = require('socket.io')(http);
var mysql_pool  = mysql.createPool({
    connectionLimit : 10,
    host            : '89.223.27.69',
    user            : 'FocusCore',
    password        : 'GG1Dn9qUIKAd53Lp',
    database        : 'focus'
});


function isJson(text) {
    return /^[\],:{}\s]*$/.test(text.replace(/\\["\\\/bfnrtu]/g, '@')
    .replace(/"[^"\\\n\r]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?/g, ']')
    .replace(/(?:^|:|,)(?:\s*\[)+/g, ''));
}

mqtt_client.on('connect', function () {
    mqtt_client.subscribe('+/report/+', {'qos': 2}, function (err) {
        if (err) {
            console.log(err);
        }
    })
})

mqtt_client.on('message', function (topic, message) {
    //console.log(topic, message.toString());

    let topic_path = topic.split('/');
    let topic_path_len = topic_path.length;
    if (topic_path_len > 0) {
        let device_name = topic_path[0];
        if (topic_path_len > 1) {
            let topic_name = topic_path[1];
            if (topic_name === 'report') {
                if (topic_path_len == 3) {
                    // передача показаний датчиков
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
                            //console.log(results)
                        })
                    } else {
                        payload = msg;
                    }
                    
                    //console.log('передача показаний датчиков', device_name, unit_name, payload);
                }
            }
        }
    }
})

// проверка ключа
app.use('*', function (req, res, next) {
    if (req.body.monitoring_key != MONITORING_KEY) {
        res.statusCode = 404;
        res.send();
        return 0;
    }

    next();
});

app.get('/', function (req, res) {
    res.statusCode = 404;
    res.send();
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

//io.use(function (socket, next) {
//	return next();
//});


io.sockets.on('connection', function (socket) {
    console.log('ws connected');
    socket.on('cmd_response', function (msg) {

    });

    socket.on('disconnect', function () {
        console.log('ws disconnected');
    });
});

http.listen(3000, function () {
    console.log('proxy server run');
});
