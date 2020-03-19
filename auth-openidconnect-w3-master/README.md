# Simple PHP project that authenticates via OpenIDConnect (IBM ID and w3ID)

# Authentication

Authentication is corrently possible via 1 technology.

  - OpenIDConnect

Todo in future:

  - SAML
  - LDAP

Currently, only one is supported and that is OpenConnectID.

### Prerequirements

- Application for openIDConnect with w3ID or IBM ID on staging or production created via http://w3.ibm.com/tools/sso
- Up to date Apache, PHP and curl installed on server

### Setting up project

1. Create file **cfg/auth_technology.inc.php** with following content:

        <?php
        //define which technology you wish to use for sign in here
        $auth_technology = "openidconnect";
        ?>

2. Create file **cfg/openidconnect.inc.php**

        <?php
        	$config_openidconnect = new stdClass();
        	$config_openidconnect->authorize_url = "given url ending with /authorize";
        	$config_openidconnect->token_url = "given url ending with /token";
        	$config_openidconnect->introspect_url = "given url ending with /introspect";
        	$config_openidconnect->client_id = "given client id";
        	$config_openidconnect->client_secret = "given client secret";
        	$config_openidconnect->redirect_url = "your approved redirect url - needs to be https, in this example auth/index.php or simply auth/";
        ?>

3. Open index.php

4. **IMPORTANT**: For use in production, uncomment line **throw new Exception('OpenIDConnect returned values were not correct.');** in **class/auth.class.php** on line number 136