'use strict';

var express = require('express');
var cors = cors = require('cors');
var app = express();
var server = require('http').createServer(app);
var io = require('socket.io').listen(server);

var consolidate = require('consolidate');

app.use(cors());
app.set('views', './public');

io.sockets.on('connection', function (socket) {
  socket.emit('news', { hello: 'world' });
  socket.on('my other event', function (data) {
    console.log(data);
  });
});

// use livereload middleware
app.use(require('grunt-contrib-livereload/lib/utils').livereloadSnippet);


app.set('port', (process.env.PORT || 5000));
app.use(express.static(__dirname + '/public'));

app.get('/', function(request, response) {
  // response.send('Hello World!');
  response.sendfile('./public/index.html');
});

app.get('/googled336ac59e4c9735b.html', function(request, response) {
  // response.send('Hello World!');
  response.sendfile('./public/index.html');
});


app.post('/addRecipe', function(req, res) {
  var url = req.params.url;
  // response.send(url);
  res.json({msg: 'This is CORS-enabled for all origins!' + url});
  console.log('addrecipe: ' + url);
});

app.listen(app.get('port'), function() {
  console.log('Node app is running at localhost:' + app.get('port'));
});

var pg = require('pg');

app.get('/db', function(request, response) {
  pg.connect(process.env.DATABASE_URL, function(err, client, done) {
    client.query('SELECT * FROM test_table', function(err, result) {
      done();
      if (err)
       { console.error(err); response.send('Error ' + err); }
      else
       { response.send(result.rows); }
    });
  });
});

exports = module.exports = server;

exports.use = function() {
  app.use.apply(app, arguments);
};
