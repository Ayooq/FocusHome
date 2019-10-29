const mysql = require('mysql2');
const path = require("path");
const yaml = require('js-yaml');
const fs   = require('fs');

const config = yaml.safeLoad(fs.readFileSync(path.join(__dirname, "../../../config.yaml"), 'utf8'));

const pool  = mysql.createPool({
    connectionLimit : config.MYSQl.connectionLimit,
    host            : config.MYSQl.host,
    user            : config.MYSQl.user,
    password        : config.MYSQl.password,
    database        : config.MYSQl.database
});

module.exports = pool;