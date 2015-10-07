#!/usr/bin/env python3

import logging
import asyncio
import urllib.parse

import click
import aiohttp
from aiohttp import web


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

@asyncio.coroutine
def main_page(request):
    text = """<a href="/login/">Login with Feide Connect</a>"""
    return web.Response(body = text.encode('utf-8'))


@asyncio.coroutine
def login_page(request):
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
    return web.HTTPFound(redirect_url)


@asyncio.coroutine
def login_success_page(request):
    # Feide Connect redirected the user here and gave us an "authorization
    # code" in the query string.
    _log.debug("login success page")
    code = request.GET.get('code', None)
    if not code:
        return web.Response(body = "No 'code' parameter, no login.".encode('utf-8'))
    # Feide Connect also sent back the "state" parameter we gave it earlier
    state = request.GET.get("state", None)
    if state != "some_opaque_string":
        return web.Response(body = "No (or wrong) 'state' parameter, no login.".
                encode('utf-8'))

    # we are now supposed to use the authorization code to get an access token
    # from Feide Connect, through a so-called "Access Token Request" HTTP POST
    # (http://tools.ietf.org/html/rfc6749#section-4.1.3 ).
    token_req_url = "https://auth.feideconnect.no/oauth/token"

    auth_header = aiohttp.helpers.BasicAuth(login = _config["client_id"],
            password = _config["client_secret"])
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
    response = yield from aiohttp.post(token_req_url,
            #data = params, headers = headers)
            data = params, auth = auth_header)
            #data = params)

    # if response's HTTP status is not 200, we must bail out
    if response.status != 200:
        error_text = yield from response.text()
        msg = "error: access token request failed. Got answer: {}".format(
                error_text)
        _log.debug(msg)
        return web.Response(body = msg.encode('utf-8'))

    # If we got a good response, we get some JSON with the access token in it.
    token_data = yield from response.json()
    _log.debug("access token request returned:\n{}\n".format(token_data))
    access_token = token_data["access_token"]


    # now we're all set. the user is authenticated, we are authorized. let's
    # just do some calls to Feide Connect and present them to the user.
    out = web.StreamResponse()
    out.content_type = "text/plain"
    out.start(request)
    out.write("Login successful. Doing some API calls now:\n\n".encode('utf-8'))
    yield from out.drain()

    queries = [ # method, url, params
            ('GET', 'https://groups-api.feideconnect.no/groups/me/groups', {}),
            ('GET', 'https://auth.dev.feideconnect.no/userinfo', {}),
            ('GET', 'https://api.feideconnect.no/peoplesearch/orgs', {}),
            ('GET', 'https://api.feideconnect.no/peoplesearch/people',
              { 'org' : 'uninett.no',
                'query' : 'andreas'}),
            ]
    headers = { "Authorization": "Bearer {}".format(access_token) }
    reqs = [ aiohttp.request(q[0], q[1], params = q[2], headers = headers)
            for q in queries ]

    for req in asyncio.as_completed(reqs):
        response = yield from req
        try:
            text = yield from response.text()
        except Exception as e:
            text = "Error: {}".format(e)

        out.write("{}\n{}\n\n\n".format(response.url, text).encode('utf-8'))
        yield from out.drain()

    yield from out.write_eof()
    return out




@asyncio.coroutine
def init_server(loop):
    app = web.Application(loop = loop)
    app.router.add_route('GET', '/', main_page)
    app.router.add_route('GET', '/login/', login_page)
    app.router.add_route('GET', '/login_success/', login_success_page)

    srv = yield from loop.create_server(
            app.make_handler(), '0.0.0.0', _config["port"])
    return srv


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
    loop = asyncio.get_event_loop()

    _config.update(kwargs)

    loop.run_until_complete(init_server(loop))
    _log.info("Service listening on port {}. Press Ctrl+C to terminate.".
            format(kwargs["port"]))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        _log.info("caught KeyboardInterrupt, terminating")



if __name__ == "__main__":
    run(auto_envvar_prefix = "FC")
