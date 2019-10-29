const mysql = require('mysql2');
const path = require("path");
const yaml = require('js-yaml');
const fs   = require('fs');

const config = yaml.safeLoad(fs.readFileSync(path.join(__dirname, "../../../config.yaml"), 'utf8'));

function connect(){
    return mysql.createConnection({
        host            : config.MYSQl.host,
        user            : config.MYSQl.user,
        password        : config.MYSQl.password,
        database        : config.MYSQl.database
    });
}

module.exports = connect;