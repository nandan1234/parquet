/*eslint-env node*/

//------------------------------------------------------------------------------
// node.js blueid sample code
//   ready for BBluemix
//   02/05/2016 mlu@us.ibm.com
//------------------------------------------------------------------------------

// This application uses express as its web server
// for more info, see: http://expressjs.com
var express = require('express');

// START OF CHANGE
var session = require('express-session');
var passport = require('passport');
var cookieParser = require('cookie-parser');
var fs = require('fs');
var https = require('https');
// END OF CHANGE

// cfenv provides access to your Cloud Foundry environment
// for more info, see: https://www.npmjs.com/package/cfenv
var cfenv = require('cfenv');

// read settings.js
var settings = require('./settings.js');
// work around intermediate CA issue
process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0"

// create a new express server
var app = express();

// Uncomment the following section if running locally
https.createServer({
        key: fs.readFileSync('key.pem'),
        cert: fs.readFileSync('certificate.pem')
}, app).listen(5000);

// START OF CHANGE
app.use(cookieParser());
app.use(session({resave: 'true', saveUninitialized: 'true' , secret: 'keyboard cat'}));
app.use(passport.initialize());
app.use(passport.session());

passport.serializeUser(function(user, done) {
	done(null, user);
});

passport.deserializeUser(function(obj, done) {
	done(null, obj);
});

var OpenIDConnectStrategy = require('passport-idaas-openidconnect').IDaaSOIDCStrategy;
var Strategy = new OpenIDConnectStrategy({
        authorizationURL : settings.authorization_url,
        tokenURL : settings.token_url,
        clientID : settings.client_id,
        scope: 'openid',
        response_type: 'code',
        clientSecret : settings.client_secret,
        skipUserProfile: true,
        issuer: settings.issuer_id,
        addCACert: true,
        callbackURL: settings.callback_url,
        CACertPathList: [
        '/oidc_w3id_staging.cer',
        '/DigiCertGlobalRootCA.crt',
        '/DigiCertSHA2SecureServerCA.crt']
        },
        function(iss, sub, profile, accessToken, refreshToken, params, done)  {
                process.nextTick(function() {
                        profile.accessToken = accessToken;
                        profile.refreshToken = refreshToken;
                        done(null, profile);
                })
        }
)

passport.use(Strategy);

app.get('/', ensureAuthenticated,function(req, res) {
});

app.get('/login', passport.authenticate('openidconnect', {}));

function ensureAuthenticated(req, res, next) {
	if (!req.isAuthenticated()) {
	        req.session.originalUrl = req.originalUrl;
		res.redirect('/login');
	} else {
		return next();
	}
}

// handle callback, if authentication succeeds redirect to
// original requested url, otherwise go to /failure
app.get('/oidc_callback',function(req, res, next) {
	
	var redirect_url = req.session.originalUrl;
	passport.authenticate('openidconnect', {
		successRedirect: redirect_url,
		failureRedirect: '/failure',
	})(req,res,next);
});

// failure page
app.get('/failure', function(req, res) {
	res.send('login failed'); });


// END OF CHANGE

// serve the files out of ./public as our main files
app.use(express.static(__dirname + '/public'));

// get the app environment from Cloud Foundry
// Comment out following line if running locally
 var appEnv = cfenv.getAppEnv();

// start server on the specified port and binding host
// Comment out following line if running locally
 app.listen(appEnv.port, function() {

// // print a message when the server starts listening
   console.log("server starting on " + appEnv.url);
 });
