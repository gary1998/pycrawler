const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const glob = require("glob");
const fs = require('fs');
const app = express();

app.use(cors());
app.use(express.json());

readFile = (file) => {
    return new Promise((resolve, reject) => {
        fs.readFile(file, (err, data) => {
            if(!err){
                resolve(data);
            } else {
                reject(err);
            }
        });
    });
}

collectFiles = (dir, targetsStr) => {
    return new Promise(async resolve => {
        let result = []
        let targets = targetsStr.split(',')
        for(var i = 0; i < targets.length; i++) {
            let files = glob.sync(`${dir}/*.${targets[i]}`);
            for(var j = 0; j < files.length; j++) {
                let def = await readFile(files[j]);
                result.push({
                    'name': files[j].split('/').slice(-1)[0],
                    'def': def.toString()
                });
            }
        }
        resolve(result);
    });
}

app.get('/', (req, res) => {
    let result = {
        'apis': '',
        'response': '',
        'errors': ''
    }
    let resp = spawn('python', ['./crawler.py', `${req.query['host']}`, `${req.query['rejections']}`, `${req.query['targets']}`, `${req.query['logging']}`]);
    resp.stdout.on('data', (data) => {
        result.response += data.toString();
    });
    resp.stderr.on('data', (err) => {
        result.errors += err.toString();
    });
    resp.on('close', (_) => {
        let data = JSON.parse(result.response);
        collectFiles(data.downloadDir, req.query['targets']).then(response => {
            res.statusCode = 200;
            result.apis = response;
            res.send(result);
        });
    });
});

const port = process.env.PORT || 3000;

app.listen(port, () => {
    console.log('server started!');
});