'use strict';


var express = require('express');
var cors = cors = require('cors');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io').listen(server);
var bodyParser = require('body-parser');
var request = require('request');
var cheerio = require('cheerio');
var models = require('./models/').setup();
var orm = require('./models/index');
var swig = require('swig');
var _ = require('lodash');
var glob = require('glob');
var closure = require('./public/js/closure-library/closure/goog/bootstrap/nodejs.js');


var assets = {
    lib: {
      css: [
        'public/js/bootstrap/dist/css/bootstrap.css',
        'public/js/bootstrap/dist/css/bootstrap-theme.css',
      ],
      js: [
        'public/js/angular/angular.js',
        'public/js/angular-resource/angular-resource.js',
        'public/js/angular-animate/angular-animate.js',
        'public/js/angular-ui-router/release/angular-ui-router.js',
        'public/js/angular-ui-utils/ui-utils.js',
        'public/js/angular-bootstrap/ui-bootstrap-tpls.js'
      ]
    },
    css: [
      'public/modules/**/css/*.css'
    ],
    js: [
      'public/config.js',
      'public/application.js',
      'public/modules/*/*.js',
      'public/modules/*/*[!tests]*/*.js'
    ]
  };

var getGlobbedFiles = function(globPatterns, removeRoot) {
  // URL paths regex
  var urlRegex = new RegExp('^(?:[a-z]+:)?\/\/', 'i');

  // The output array
  var output = [];

  // If glob pattern is array so we use each pattern in a recursive way, otherwise we use glob
  if (_.isArray(globPatterns)) {
    globPatterns.forEach(function(globPattern) {
      output = _.union(output, getGlobbedFiles(globPattern, removeRoot));
    });
  } else if (_.isString(globPatterns)) {
    if (urlRegex.test(globPatterns)) {
      output.push(globPatterns);
    } else {
      glob(globPatterns, {
        sync: true
      }, function(err, files) {
        if (removeRoot) {
          files = files.map(function(file) {
            return file.replace(removeRoot, '');
          });
        }

        output = _.union(output, files);
      });
    }
  }
  return output;
};

/**
 * Get the modules JavaScript files
 */
var getJavaScriptAssets = function(includeTests) {
  var output = getGlobbedFiles(assets.lib.js.concat(assets.js), 'public/');

  // To include tests
  if (includeTests) {
    output = _.union(output, getGlobbedFiles(assets.tests));
  }

  return output;
};

/**
 * Get the modules CSS files
 */
var getCSSAssets = function() {
  var output = getGlobbedFiles(assets.lib.css.concat(assets.css), 'public/');
  return output;
};

goog.require('goog.string');


var Recipe = orm.model('Recipe');
var Ingredient = orm.model('Ingredient');

var consolidate = require('consolidate');

app.use(bodyParser.urlencoded({
  extended: true
}));

app.use(bodyParser.json({
  extended: true
}));
app.use(cors());

// Rendering engine and global variables
app.engine('html', swig.renderFile);
app.set('view engine', 'html');
app.set('views', 'views');
app.locals.something = 'som....';
app.locals.jsFiles = getJavaScriptAssets(false);
app.locals.cssFiles = getCSSAssets();

io.sockets.on('connection', function(socket) {
  socket.emit('news', { hello: 'world' });
  socket.on('my other event', function(data) {
    console.log(data);
  });
});

app.set('port', (process.env.PORT || 5000));
app.use(express.static(__dirname + '/public'));
app.use(express.static(__dirname + '/node_modules'));

app.get('/', function(request, response) {
  response.render('index.html', {recipes: [1, 2, 3, 4, 'jdkla']});
});

app.get('/googled336ac59e4c9735b.html', function(request, response) {
  // response.send('Hello World!');

  Recipe.find({id: req.query.id}).success(function(r) {
    response.sendfile('./public/index.html', {recipes: r});
  });

});


app.post('/addRecipe', function(req, res) {
  var url = req.body.url;
  request(url, function(error, response, html) {
    if (!error) {
      var $ = cheerio.load(html);
      var ingredients = getElements($, 'ingredients');
      var instructions = getElements($, 'recipeInstructions');
      var title = $('[itemprop=name]')[0].children[0].data;
      var image = $('[itemprop=image]')[0].attribs.src;
      Recipe.findOrCreate({where: {url: url, image: image, title: title}}).success(function(recipe, o) {
        console.log(recipe);
        for (var i = 0; i < ingredients.length; i++) {
          var is = [];
          var ingredientName = goog.string.collapseWhitespace(ingredients[i]);
          Ingredient.findOrCreate({where: {name: ingredientName}})
              .success(function(ingredient, o) {
                recipe.addIngredient(ingredient);
                is.push(ingredient);
                if (is.length == ingredients.length) {
                  res.json({instructions: instructions, ingredients: ingredients});
                }
              });
        }
      });
    }
  });
});

var getElements = function($, type) {
  var elements = $('[itemprop=' + type + ']');
  var values = [];
  for (var i = 0; i < elements.length; i++) {
    var children = elements[i].children;
    var s = [];
    traverse(children, s);
    values.push(s.join(' '));
  }
  return values;
};

var traverse = function(nodes, s) {
  for (var i = 0; i < nodes.length; i++) {
    if (nodes[i].children) {
      traverse(nodes[i].children, s);
    } else {
      s.push(nodes[i].data);
    }
  }
};

app.listen(app.get('port'), function() {
  console.log('Node app is running at localhost:' + app.get('port'));
});

app.get('/addRecipe2', function(req, res) {
  var chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ';
  var rString = req.query.recipe;
  Recipe.findOrCreate({where: {url: rString, image: 'someimage'}}).success(function(recipe, o) {
    console.log(recipe);
    for (var i = 0; i < 5; i++) {
      var iString = 'abc';
      var is = [];
      Ingredient.findOrCreate({where: {name: iString}})
        .success(function(ingredient, o) {
          recipe.addIngredient(ingredient);
          is.push(ingredient);
          if (is.length == 5) {
            res.send(is);
          }
      });
    }
  });
});

app.get('/getRecipe', function(req, res) {
  // var rs = [];
  // if (!req.query.id) {
  //   Recipe.findAll().success(function(recipes, o) {
  //     for (var i = 0; i < recipes.length; i++) {
  //       rs.push(recipes[i]);
  //       recipes[i].getIngredients.success(function(is) {
  //         rs.push(is);
  //         if (rs.length == recipes.length) {
  //           res.send(rs);
  //         }
  //       });
  //     }
  //   });
  // }
  // Recipe.find(req.query.id).success(function(recipe) {
  //   // var is = [];
  //   // console.log(recipe.getIngredients);
  //   recipe.getIngredients().success(function(is) {
  //     res.send(is);
  //   });
  //   // res.send(recipe);
  // });
  Recipe.find({id: req.query.id}).success(function(r) {
    res.json(r);
  });
});

app.get('/getRecipes', function(req, res) {
  Recipe.findAll().success(function(recipes) {
    var all = [];
    var allIs = [];
    for (var i = 0; i < recipes.length; i++) {
      var recipe = recipes[i].dataValues;
        all.push({id: recipe.id,
          url: recipe.url,
          image: recipe.image,
          title: recipe.title,
          ingredients: []});
      recipes[i].getIngredients().success(function(ingredients) {
        var is = [];
        for (var j = 0; j < ingredients.length; j++) {
          is.push(ingredients[j].dataValues.name);
        }
        allIs.push(is);
        if (allIs.length == recipes.length) {
          for (var j = 0; j < recipes.length; j++) {
            all[j].ingredients = allIs[j];
          }
          res.render('index', {recipes: all});
        }
      });
    }
  });
});

exports = module.exports = server;

exports.use = function() {
  app.use.apply(app, arguments);
};

