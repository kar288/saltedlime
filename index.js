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
var closure =
  require('./public/js/closure-library/closure/goog/bootstrap/nodejs.js');
var session = require('express-session');
var cookieParser = require('cookie-parser');
var consolidate = require('consolidate');
var passport = require('passport');
var GoogleStrategy = require('passport-google-oauth').OAuth2Strategy;


var assets = {
    lib: {
      css: [
        'public/js/bootstrap/dist/css/bootstrap.css',
        'public/js/bootstrap/dist/css/bootstrap-theme.css'
      ],
      js: [
        'public/js/angular/angular.js',
        'public/js/angular-resource/angular-resource.js',
        'public/js/angular-animate/angular-animate.js',
        'public/js/angular-ui-router/release/angular-ui-router.js',
        'public/js/angular-ui-utils/ui-utils.js',
        'public/js/angular-bootstrap/ui-bootstrap-tpls.js',
        'publice/js/jquery/dis/jquery.js'
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

  // If glob pattern is array so we use each pattern in a recursive way,
  // otherwise we use glob
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
goog.require('goog.dom');

var GOOGLE_CLIENT_ID =
  '788135140677-2vnmeqsbec9jrviu10l61i69sg3p2u3b.apps.googleusercontent.com';
var GOOGLE_CLIENT_SECRET = 'vEvB3JGlpymsNDG6ADeDb3nu';

app.use(session({
  genid: function(req) {
    return '1234';
  },
  secret: 'keyboard cat'
}));


app.use(bodyParser.urlencoded({
  extended: true
}));

app.use(bodyParser.json({
  extended: true
}));
app.use(cors());

app.use(express.static(__dirname + '/public'));
app.use(express.static(__dirname + '/node_modules'));
app.use(cookieParser());

passport.serializeUser(function(user, done) {
  done(null, user.id);
});

passport.deserializeUser(function(id, done) {
  User.find(id)
    .success(function(user) {
        done(null, user);
    }).error(function(err) {
        done(new Error('User ' + id + ' does not exist'));
    });
});

app.use(passport.initialize());
app.use(passport.session());

passport.use(new GoogleStrategy({
    clientID: GOOGLE_CLIENT_ID,
    clientSecret: GOOGLE_CLIENT_SECRET,
    callbackURL: '/auth/google/callback'
  },
  function(accessToken, refreshToken, profile, done) {
    console.log('logging in');
    var profile = profile._json;
    User.findOrCreate({where: {
      googleId: profile.id,
      googleEtag: profile.etag,
      picture: profile.image.url,
      name: profile.displayName}})
    .success(function(user) {
      return done(null, user[0].dataValues);
    }).error(function(err) {
      return done(err);
    });
  }
));

var Recipe = orm.model('Recipe');
var Ingredient = orm.model('Ingredient');
var User = orm.model('User');


// Rendering engine and global variables
app.engine('html', swig.renderFile);
app.set('view engine', 'html');
app.set('views', 'views');
app.locals.env = process.env.NODE_ENV;
app.locals.fbAppId =
  process.env.NODE_ENV ? '628807420552479' : '628799940553227';

app.locals.jsFiles = getJavaScriptAssets(false);
app.locals.cssFiles = getCSSAssets();

io.sockets.on('connection', function(socket) {
  socket.emit('news', { hello: 'world' });
  socket.on('my other event', function(data) {
    console.log(data);
  });

});

app.set('port', (process.env.PORT || 5000));

app.get('/', function(request, response) {
  var user = request.user ? request.user.dataValues.name : null;
  response.render('index.html', {user: user});
});

app.get('/googled336ac59e4c9735b.html', function(request, response) {
  Recipe.find({id: req.query.id}).success(function(r) {
    response.sendfile('./public/index.html', {recipes: r});
  });
});


app.get('/account', ensureAuthenticated, function(req, res) {
  res.render('account', { user: req.user });
});

app.get('/login', function(req, res) {
  res.render('login', { user: req.user });
});

// GET /auth/google
//   Use passport.authenticate() as route middleware to authenticate the
//   request.  The first step in Google authentication will involve
//   redirecting the user to google.com.  After authorization, Google
//   will redirect the user back to this application at /auth/google/callback
app.get('/auth/google',
  passport.authenticate('google',
    {scope: ['https://www.googleapis.com/auth/plus.login']}),
  function(req, res) {
    // The request will be redirected to Google for authentication, so this
    // function will not be called.
  });

// GET /auth/google/callback
//   Use passport.authenticate() as route middleware to authenticate the
//   request.  If authentication fails, the user will be redirected back to the
//   login page.  Otherwise, the primary route function function will be called,
//   which, in this example, will redirect the user to the home page.
app.get('/auth/google/callback',
  passport.authenticate('google', { failureRedirect: '/login' }),
  function(req, res) {
    res.redirect('/');
    // res.json('');
  });

app.get('/logout', function(req, res) {
  req.logout();
  res.redirect('/');
});

// Simple route middleware to ensure user is authenticated.
//   Use this route middleware on any resource that needs to be protected.  If
//   the request is authenticated (typically via a persistent login session),
//   the request will proceed.  Otherwise, the user will be redirected to the
//   login page.
function ensureAuthenticated(req, res, next) {
  if (req.isAuthenticated()) { return next(); }
  res.redirect('/auth/google');
}


app.get('/addRecipes', function(req, res) {
  var recipes = [{"url":"http://www.thekitchn.com/recipe-spiced-lentil-sweet-potato-and-kale-whole-wheat-pockets-181100"},{"url":"http://www.thekitchn.com/recipe-simple-kale-potato-soup-weeknight-dinner-recipes-from-the-kitchn-13802"},{"url":"http://www.bbcgoodfood.com/recipes/cabbage-red-rice-salad-tahini-dressing"},{"url":"http://www.bbcgoodfood.com/recipes/courgette-couscous-salad-tahini-dressing"},{"url":"http://www.bbcgoodfood.com/recipes/coleslaw-tahini-yogurt-dressing"},{"url":"http://www.bbcgoodfood.com/recipes/1901/roast-tomatoes-with-asparagus-and-black-olives"},{"url":"http://www.bbcgoodfood.com/recipes/3151/mozzarella-tomato-and-black-olive-tarts"}];
  for (var i = 0; i < recipes; i++) {
    addRecipe(recipes[i], true /* sendResponse */, res,
    function(res, recipe) {
      res.json(recipe);
    });
  }
});


app.post('/addRecipe', function(req, res) {
  addRecipe(req.body.url, true /* sendResponse */, res,
    function(res, recipe) {
      var id = req.user ? req.user.dataValues.id : null;
      if (id) {
        User.find(id).success(function(user) {
          user.addRecipe(recipe);
          res.json(recipe);
        });
      } else {
        res.json(null);
      }
    });
});

var addRecipe = function(url, sendResponse, res, callback) {
  request(url, function(error, response, html) {
    if (!error) {
      var $ = cheerio.load(html);
      var ingredients = getElements($, 'ingredients');
      var instructions = getElements($, 'recipeInstructions');
      var title = $('[itemprop=name]')[0].children[0].data;
      var image = getImage($);

      Recipe.findOrCreate({where:
        {url: url, image: image, title: title}})
      .success(function(recipe, o) {
        for (var i = 0; i < ingredients.length; i++) {
          var is = [];
          var ingredientName = goog.string.collapseWhitespace(ingredients[i]);
          Ingredient.findOrCreate({where: {name: ingredientName}})
            .success(function(ingredient, o) {
              recipe.addIngredient(ingredient);
              is.push(ingredient);
              if (is.length == ingredients.length && sendResponse) {
                return callback(res, recipe);
              }
            });
        }
      });
    }
  });
};

var getImage = function($) {
  var elements = $('[itemprop=image]');
  for (var i = 0; i < elements.length; i++) {
    var parent = goog.dom.getAncestor(elements[i], function(el) {
      var type = el.attribs.itemtype;
      if (type == undefined) {
        return null;
      }
      return goog.string.contains(type, 'Recipe');
    });
    if (parent === null) {
      return elements[i].attribs.src;
    }
  }
  var recipe = goog.dom.findNode($('body')[0], function(el) {
    var type = el.attribs ? el.attribs.itemtype : null;
    return type && goog.string.contains(type, 'Recipe');
  });
  var image = goog.dom.findNode(recipe, function(el) {
    return el.name == 'img';
  });
  if (image) {
    return image.attribs.src;
  }
  return null;
};

var getElements = function($, type) {
  var elements = $('[itemprop=' + type + ']');
  var values = [];
  for (var i = 0; i < elements.length; i++) {
    var children = elements[i].children;
    var s = [];
    traverse(children, s);
    values.push(goog.string.collapseWhitespace(s.join(' ')));

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

app.get('/getRecipe', function(req, res) {
  Recipe.find({where: {id: req.query.id}}).success(function(r) {
    res.json(r);
  });
});

app.get('/getUser', function(req, res) {
  User.find({where: {id: req.query.id}}).success(function(user) {
    if (!user) {
      res.json('');
    }
    user.getRecipes().success(function(recipes) {
      res.json(recipes);
    });
  });
});

app.get('/getUsers', ensureAuthenticated, function(req, res) {
  User.findAll().success(function(users) {
    res.json(users);
  });
});


app.get('/allRecipeUrls', function(req, res) {
  Recipe.all({attributes: ['url']}).success(function(r) {
    res.json(r);
  });
});

app.get('/getRecipes', function(req, res) {
  var id = req.user ? req.user.dataValues.id : -1;
  User.find({where: {id: id}}).success(function(user) {
    if (!user) {
      res.render('index');
      return;
    }
    user.getRecipes().success(function(recipes) {
      var all = {};
      var allIs = [];
      for (var i = 0; i < recipes.length; i++) {
        var recipe = recipes[i].dataValues;
          all[recipe.id] = {url: recipe.url,
            image: recipe.image,
            title: recipe.title,
            ingredients: []};
        recipes[i].getIngredients().success(function(ingredients) {
          var is = [];
          var recipeId = ingredients[0].IngredientRecipe.dataValues.RecipeId;
          for (var j = 0; j < ingredients.length; j++) {
            is.push(ingredients[j].dataValues.name);
          }
          allIs.push({ingredients: is, recipeId: recipeId});
          if (allIs.length == recipes.length) {
            var rs = {};
            for (var j = 0; j < recipes.length; j++) {
              var r = all[allIs[j].recipeId];
              rs[allIs[j].recipeId] = {url: r.url,
                image: r.image,
                title: r.title,
                ingredients: allIs[j].ingredients};
            }
            res.render('index',
              {recipes: rs, user: req.user ? req.user.dataValues.name : null});
          }
        });
      }
    }).error(function() {
      res.render('index');
    });
  });
});

exports = module.exports = server;

exports.use = function() {
  app.use.apply(app, arguments);
};
