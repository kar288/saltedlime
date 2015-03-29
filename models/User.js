//Getting the orm instance
var orm = require('../models'),
    Seq = orm.Seq();

//Creating our module
module.exports = {
    model: {
        name: Seq.STRING,
        fb: {type: Seq.STRING, unique: true},
        email: {type: Seq.STRING, unique: true},
        password: Seq.STRING
    },
    relations: {
        hasMany: 'Recipe'
    },
    options: {
        freezeTableName: true
    }
};
