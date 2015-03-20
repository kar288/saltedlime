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
var closure = require('./public/js/closure-library/closure/goog/bootstrap/nodejs.js');

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
app.set('views', './public');

io.sockets.on('connection', function(socket) {
  socket.emit('news', { hello: 'world' });
  socket.on('my other event', function(data) {
    console.log(data);
  });
});

app.set('port', (process.env.PORT || 5000));
app.use(express.static(__dirname + '/public'));

app.get('/', function(request, response) {

  response.sendfile('./public/index.html');
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
      res.json({instructions: instructions, ingredients: ingredients});
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
  var rString = req.query.recipe || randomString(32, chars);

  Recipe.findOrCreate({where: {url: rString, image: 'someimage'}}).success(function(recipe, o) {
    console.log(recipe);
    for (var i = 0; i < 5; i++) {
      var iString = randomString(3, 'abc');
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
  Recipe.findAll().success(function(r) {
    res.json(r);
  });
});

function randomString(length, chars) {
    var result = '';
    for (var i = length; i > 0; --i) result += chars[Math.round(Math.random() * (chars.length - 1))];
    return result;
}
app.get('/db', function(request, response) {
  response.send('kla')
});

exports = module.exports = server;

exports.use = function() {
  app.use.apply(app, arguments);
};
