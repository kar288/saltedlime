var filesystem = require('fs');
var models = {};
var relationships = {};

var singleton = function singleton() {
    var Sequelize = require('sequelize');
    var sequelize = null;
    var modelsPath = './models';
    this.setup = function(path, database, username, password, obj) {
        // modelsPath = path;
        // if(arguments.length == 3){
    //     //     sequelize = new Sequelize(database, username);
    //     // }
    //     // else if(arguments.length == 4){
    //     //     sequelize = new Sequelize(database, username, password);
    //     // }
    //     // else if(arguments.length == 5){
    //     //     sequelize = new Sequelize(database, username, password, obj);
    //     // }

        if (process.env.DATABASE_URL) {
          sequelize = new Sequelize(process.env.DATABASE_URL);
        } else {
          sequelize = new Sequelize('kar288', 'kar288', '', {
            host: 'localhost',
            dialect: 'postgres',

            pool: {
              max: 5,
              min: 0,
              idle: 10000
            }
          });
        }
        init();
    };

    this.model = function(name) {
        return models[name];
    };

    this.Seq = function() {
        return Sequelize;
    };

    function init() {
      filesystem.readdirSync(modelsPath)
      .filter(function(file) {
        return (file.indexOf('.') !== 0) && (file !== 'index.js');
      }).forEach(function(name) {
        var object = require('.' + modelsPath + '/' + name);
        var options = object.options || {};
        var modelName = name.replace(/\.js$/i, '');
        models[modelName] =
          sequelize.define(modelName, object.model, options);
        if ('relations' in object) {
            relationships[modelName] = object.relations;
        }
      });
      for (var name in relationships) {
          var relation = relationships[name];
          for (var relName in relation) {
              var related = relation[relName];
              models[name][relName](models[related]);
          }
      }
      // sequelize.sync({force: true});
      sequelize.sync();
    }
    if (singleton.caller != singleton.getInstance) {
        throw new Error('This object cannot be instanciated');
    }
};

singleton.instance = null;

singleton.getInstance = function() {
  if (this.instance === null) {
    this.instance = new singleton();
  }
  return this.instance;
};

module.exports = singleton.getInstance();
