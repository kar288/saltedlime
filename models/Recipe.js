//Getting the orm instance
var orm = require('../models'),
    Seq = orm.Seq();

//Creating our module
module.exports = {
    model: {
        url: Seq.STRING,
        image: Seq.STRING
    },
    relations: {
        hasMany: 'Ingredient'
    },
    options: {
        freezeTableName: true
    }
};
