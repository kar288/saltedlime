"use strict";

module.exports = {
  up: function(migration, DataTypes, done) {
    migration.addColumn('Recipe', 'image', DataTypes.STRING);
    // add altering commands here, calling 'done' when finished
    done();
  },

  down: function(migration, DataTypes, done) {
    migration.removeColumn('Recipe', 'image');
    // add reverting commands here, calling 'done' when finished
    done();
  }
};
