//Getting the orm instance
var orm = require('../models'),
    Seq = orm.Seq();

//Creating our module
module.exports = {
    model: {
        name: Seq.STRING,
        googleId: {type: Seq.STRING, unique: true},
        email: {type: Seq.STRING, unique: true},
        password: Seq.STRING,
        picture: {type: Seq.STRING, unique: true},
        googleEtag: {type: Seq.STRING, unique: true}
    },
    relations: {
        hasMany: 'Recipe'
    },
    options: {
        freezeTableName: true
    }
};
