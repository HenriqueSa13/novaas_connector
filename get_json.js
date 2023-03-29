'use strict';

const fs = require('fs');

fs.readFile('http___smart_festo_com_id_instance_aas_5140_0142_3091_4340.aas.json', (err, data) => {
    if (err) throw err;
    let aas = JSON.parse(data);
    console.log(aas);
});