#!/usr/bin/env python3

import logging
import asyncio

import click
from aiohttp import web
from aioauth_client import OAuth2Client


_config = {
        # the following parameters identify our client and can be taken from
        # the Feide Connect Dashboard. The concrete values here are not valid,
        # so replace them with your own.
        "client_id" : "f1343f3a-79cc-424f-9233-5fe33f8bbd56", # ENTER YOUR CLIENT ID HERE
        "client_secret": "c6217e17-1e32-41b7-a597-e852cec0eaf3", # ENTER YOUR CLIENT SECRET HERE
        "scopes" : "peoplesearch openid userinfo userinfo-mail userinfo-feide userinfo-photo groups", # ENTER YOUR SCOPES HERE
        "port": 8000,
        }
_log = logging.getLogger(__name__)


### OAuth2 client for Feide Connect

class FeideConnectClient(OAuth2Client):
    """OAuth2 client for Feide Connect. This is still generic, not tied to our
    example app. The app-specific information comes into play only when we
    instantiate this.

    * Dashboard: https://dashboard.feideconnect.no
    * Docs: http://feideconnect.no/docs/authorization/
    * API reference: N/A
    """

    access_token_url = "https://auth.feideconnect.no/oauth/token"
    authorize_url = "https://auth.feideconnect.no/oauth/authorization"
    #base_url = ""
    name = "Feide Connect"
    user_info_url = "https://auth.feideconnect.no/userinfo"

    @staticmethod
    def user_parse(data):
        user = data.get('user')
        yield 'id', user.get('userid')
        yield 'id_sec', user.get('userid_sec')[0] # "feide:abc123@uit.no"
        yield 'name', user.get('name')
        yield 'email', user.get('email')
        yield 'picture', user.get('profilephoto')

connect_oauth = None # instantiated in init_server


### HTTP handlers, ordered by OAuth2 flow

@asyncio.coroutine
def main_page(request):
    text = """<a href="/login/">Login with Feide Connect</a>"""
    return web.Response(body = text.encode('utf-8'))


@asyncio.coroutine
def login_page(request):
    # we want the user to log in using Feide Connect, so we'll redirect her
    # there. Feide Connect will later redirect her back to us, to a URL we
    # configured on the Connect Dashboard (/login_success/).
    # we also want to have access to some information about the user, so we
    # pass the "scopes" we want to Feide Connect. We can only use scopes that
    # we have configured on the Connect Dashboard.
    redirect_url = connect_oauth.get_authorize_url(
            scope = _config["scopes"]
            )
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

    # we can use that code to get an access token from Feide Connect. Even a
    # maliciously forged 'code' parameter should not be problematic here (in
    # theory). If something went wrong, connect_oauth raises a
    # web.HTTPBadRequest, which is nice.
    token, data = yield from connect_oauth.get_access_token(code)
    assert token
    _log.debug("got bearer token {}".format(data))

    # now we can get some info about the user from Feide Connect.
    response = yield from connect_oauth.request(
            'GET', 'https://auth.feideconnect.no/userinfo')
    body = yield from response.read()
    return web.Response(body = body, content_type = 'application/json')



@asyncio.coroutine
def init_server(loop):
    app = web.Application(loop = loop)
    app.router.add_route('GET', '/', main_page)
    app.router.add_route('GET', '/login/', login_page)
    app.router.add_route('GET', '/login_success/', login_success_page)

    global connect_oauth
    connect_oauth = FeideConnectClient(
            client_id = _config["client_id"],
            client_secret = _config["client_secret"],
            # the redirect_uri parameter is optional in OAuth, but not in
            # OpenID, which Feide Connect also supports. If you enable OpenID
            # by specifying the "openid" scope in get_authorize_url, you must have
            # this (and perhaps even more!)
            redirect_uri = "http://localhost:{}/login_success/".format(_config["port"])
            )

    srv = yield from loop.create_server(
            app.make_handler(), '0.0.0.0', _config["port"])
    return srv


### Program start and main loop

@click.command()
@click.option("--port", "-p", type = int, default = _config["port"],
        help = "Port the service listens on.")
def run(port):
    """Minimalistic service using Feide Connect for OAuth2 login.
    Press Ctrl+C to terminate.
    """
    logging.basicConfig(level = logging.DEBUG)
    loop = asyncio.get_event_loop()

    _config["port"] = port

    loop.run_until_complete(init_server(loop))
    _log.info("Service listening on port {}. Press Ctrl+C to terminate.".format(port))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        _log.info("caught KeyboardInterrupt, terminating")



if __name__ == "__main__":
    run()
