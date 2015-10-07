#!/usr/bin/env python3

import logging
import urllib.parse

import click
import bottle
import requests


_config = {
        # client id and secret identify our client to Feide Connect and can be
        # obtained on the Feide Connect Dashboard. The concrete values here are
        # not valid, so replace them with your own or configure them at
        # runtime.
        "client_id" : "f1343f3a-79cc-424f-9233-5fe33f8bbd56",
        "client_secret": "c6217e17-1e32-41b7-a597-e852cec0eaf3",
        "scopes" : "peoplesearch openid userinfo userinfo-mail userinfo-feide userinfo-photo groups", # ENTER YOUR SCOPES HERE
        "port": 8000,
        }
_log = logging.getLogger(__name__)


### HTTP handlers, ordered by OAuth2 flow

@bottle.route("/")
def main_page():
    return """<a href="/login/">Login with Feide Connect</a>"""


@bottle.route("/login/")
def login_page():
    # we want the user to log in using Feide Connect, so we'll redirect her
    # there. In OAuth parlance, this constitutes an "Authorization Request"
    # (check http://tools.ietf.org/html/rfc6749#section-4.1.1 ).
    # Feide Connect will later redirect her back to us, to a URL we configured
    # on the Connect Dashboard (/login_success/ in this case).
    auth_url = "https://auth.feideconnect.no/oauth/authorization"
    params = {
            "response_type": "code",
                # specifies the OAuth workflow ("grant type") to use.
                # Server-based apps usually use "code".

            "client_id": _config["client_id"],

            "redirect_uri": "http://localhost:{}/login_success/".format(
                _config["port"]),
                # this parameter is optional. The URL must be one that is also
                # registered on the Feide Connect Dashboard.

            "scope": _config["scopes"],
                # this optional parameter defines what information we want to
                # be authorized to see. We can only use scopes that we have
                # configured on the Connect Dashboard.

            "state": "some_opaque_string",
                # this optional parameter can be used to map a request we make
                # here to the redirect Feide Connect does later. Feide Connect
                # will send that parameter back to us then. It is not
                # mandatory, but recommended to do this, to prevent cross-site
                # request forgery.
            }

    redirect_url = "{}?{}".format(auth_url, urllib.parse.urlencode(params))

    _log.debug("login page redirects user to {}".format(redirect_url))
    return bottle.redirect(redirect_url)


@bottle.route("/login_success/")
def login_success_page():
    # Feide Connect redirected the user here and gave us an "authorization
    # code" in the query string.
    _log.debug("login success page")
    code = bottle.request.params.get('code', None)
    if not code:
        return "No 'code' parameter, no login."
    # Feide Connect also sent back the "state" parameter we gave it earlier
    state = bottle.request.params.get("state", None)
    if state != "some_opaque_string":
        return "No (or wrong) 'state' parameter, no login."

    # we are now supposed to use the authorization code to get an access token
    # from Feide Connect, through a so-called "Access Token Request" HTTP POST
    # (http://tools.ietf.org/html/rfc6749#section-4.1.3 ).
    token_req_url = "https://auth.feideconnect.no/oauth/token"

    auth = requests.auth.HTTPBasicAuth(_config["client_id"], _config["client_secret"])
    # the client (i.e. we) have to send both the client id and the client secret to
    # Feide Connect. This can be done either with an HTTP basic auth header, or by
    # including a client_secret post parameter. We do the HTTP basic auth header.

    params = {
            "client_id": _config["client_id"],
                # this parameter must always be specified, no matter whether we
                # send basic auth headers or not

            #"client_secret": _config["client_secret"],
                # this one we need only if we don't send an auth header

            "grant_type": "authorization_code",
            "code": code,

            "redirect_uri": "http://localhost:{}/login_success/".format(
                _config["port"]),
                # if this parameter was given in the authorization request
                # earlier, it must also be given here, and the value must be
                # the same
            }
    _log.debug("POSTing access token request with code {} to {}".format(
        code, token_req_url))
    response = requests.post(token_req_url, params = params, auth = auth) 

    # if response's HTTP status is not 200, we must bail out
    if response.status_code != 200:
        error_text = response.text
        msg = "error: access token request failed. Got answer: {}".format(
                error_text)
        _log.debug(msg)
        return msg

    # If we got a good response, we get some JSON with the access token in it.
    token_data = response.json()
    _log.debug("access token request returned:\n{}\n".format(token_data))
    access_token = token_data["access_token"]


    # now we're all set. the user is authenticated, we are authorized. let's
    # just do some calls to Feide Connect and present them to the user.
    out = ""
    bottle.response.content_type = "text/plain"
    out += "Login successful. Doing some API calls now:\n\n"

    queries = [ # method, url, params
            ('GET', 'https://groups-api.feideconnect.no/groups/me/groups', {}),
            ('GET', 'https://auth.dev.feideconnect.no/userinfo', {}),
            ('GET', 'https://api.feideconnect.no/peoplesearch/orgs', {}),
            ('GET', 'https://api.feideconnect.no/peoplesearch/people',
              { 'org' : 'uninett.no',
                'query' : 'andreas'}),
            ]
    headers = { "Authorization": "Bearer {}".format(access_token) }
    responses = [ requests.request(q[0], q[1], params = q[2], headers = headers)
            for q in queries ]

    for response in responses:
        out += "{}\n{}\n\n\n".format(response.url, response.text)

    return out




### Program start and main loop

@click.command()
@click.option("--port", "-p", type = int, default = _config["port"],
        help = "Port the service listens on.")
@click.option("--client-id", default = _config["client_id"],
        help = "Feide Connect client ID (get on Feide Connect Dashboard).")
@click.option("--client-secret", default = _config["client_secret"],
        help = "Feide Connect client secret (get on Feide Connect Dashboard).")
def run(**kwargs): # kwargs are port, client_id, client_secret
    """Minimalistic service using Feide Connect for OAuth2 login.
    Press Ctrl+C to terminate.
    """
    logging.basicConfig(level = logging.DEBUG)

    _config.update(kwargs)

    _log.info("Starting service on port {}. Press Ctrl+C to terminate.".
            format(kwargs["port"]))

    try:
        bottle.run(host = "0.0.0.0", port = _config["port"], debug = True)
    except KeyboardInterrupt:
        _log.info("caught KeyboardInterrupt, terminating")



if __name__ == "__main__":
    run(auto_envvar_prefix = "FC")
