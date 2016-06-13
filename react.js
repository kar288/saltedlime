var fs = require("fs");
var browserify = require("browserify");
browserify("recipes/static/js/dayMenu.js")
  .transform("babelify", {presets: ["es2015", "react"]})
  .bundle()
  .pipe(fs.createWriteStream("recipes/static/js/bundle.js"));
