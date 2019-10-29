const { Worker } = require("worker_threads");
const path = require("path");
const zlib = require('zlib');
const fs = require('fs');

let buffer = zlib.gzipSync(`
    .1.3.6.1.2.1.2.2.1.2.1 = STRING: "eth0"
    .1.3.6.1.2.1.2.2.1.3.1 = INTEGER: 6
    .1.3.6.1.2.1.2.2.1.4.1 = INTEGER: 1500
    .1.3.6.1.2.1.2.2.1.5.1 = Gauge32: 100000000
    .1.3.6.1.2.1.2.2.1.6.1 = Hex-STRING: 00 C0 EE DB B7 E2
    .1.3.6.1.2.1.2.2.1.7.1 = INTEGER: 1
    .1.3.6.1.2.1.2.2.1.8.1 = INTEGER: 1
`);

//buffer = zlib.gzipSync(fs.readFileSync('/var/www/servers/focus_web_app/docs/device_image_20190820124348.txt'));

let worker = new Worker(
    path.join(__dirname, "./snmp-worker.js"),
    {
        'workerData': {
            'action': 'snmp_set_image',
            'device_name': 'FP-2',
            'buffer': buffer
        }
    }
);

worker.on("message", (msg) => {
    console.log(msg);
});
worker.on("error", (error) => console.error("error", error));
worker.on("exit", (code) => console.log("exit", code));