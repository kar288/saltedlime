//Getting the orm instance
var orm = require('../models'),
    Seq = orm.Seq();

//Creating our module
module.exports = {
    model: {
        q: Seq.STRING,
        name: Seq.STRING
    },
    relations: {
        hasMany: 'Recipe'
    },
    options: {
        freezeTableName: true
    }
};
