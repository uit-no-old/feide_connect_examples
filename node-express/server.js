var express = require('express');
var url = require('url');
var config = require("./config.js");
var passport = require('passport');
var feide_passport = require('passport-feideconnect-oauth2');

var app = express();
passport.use(new feide_passport.Strategy({
        clientID: config.CLIENT_ID,
        clientSecret: config.CLIENT_SECRET,
        callbackURL: config.REDIRECT_URI
    },
    function(accessToken, refreshToken, profile, done) {

        console.log(profile);
        console.log(accessToken);
        console.log(refreshToken);
        console.log(done);
        return done(null, accessToken);

    }
));

app.use(passport.initialize());
app.set('views', __dirname + '/views');
app.set('view engine', 'jade');

app.get('/login/', passport.authorize('feideconnect'),
  function (req, res) {
  res.render('home',
    { title : 'Welcome to Feide Connect Chat',
      token : req.account
     }
  )
});

app.use(express.static('public'));

app.listen(3000);
console.log('Listening on port 3000...');