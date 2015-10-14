# Some Feide Connect examples and info

In here: some example apps and a bit of info about using [Feide Connect](http://feideconnect.no/). Contributions welcome!


## Utviklerlunsj presentation

This whole thing was started when preparing a presentation about Connect for developers at the University of Tromsø. You can find the presentation [here](https://docs.google.com/presentation/d/1QcMZA4vJi_3WGzimr6jcNo3X03hq27ZJlGid4Tqdci8/edit?usp=sharing) on Google Slides.


## Examples

* Python backends (OAuth2 clients)
    * [py-bottle-requests](py-bottle-requests/): blocking webserver using the [Bottle](http://bottlepy.org) web framework and the [requests](http://python-requests.org) HTTP client library. No OAuth library.
    * [py-aiohttp](py-aiohttp/): asynchronous webserver with [asyncio](https://docs.python.org/3/library/asyncio.html) (Python 3.4+). Using the [aiohttp](http://aiohttp.readthedocs.org/en/stable/index.html) HTTP client/server. No OAuth library.
    * [py-aiohttp-aioauth](py-aiohttp-aioauth/): Like the above, but using an OAuth client plugin for aiohttp, [aioauth\_client](https://github.com/klen/aioauth-client).
* Java backends
    * TODO (Espen wrote one. Include or link it.)

## Recommended reading

* [https://aaronparecki.com/articles/2012/07/29/1/oauth2-simplified](Quick intro to using OAuth that doesn't suck)
