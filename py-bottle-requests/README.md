## aiohttp example service using Feide Connect

Minimalistic service written in Python3 using the aiohttp server. Just lets a user log in and prints some info it can get about the user.


### Configure it

You need to configure at least the Feide Connect client ID and secret (get these on the [Feide Connect Dashboard](https://dashboard.feideconnect.no/)). You can do this in any of the following ways:
- use the `--client-id` and `--client-secret` command line options
- set `FC_CLIENT_ID` and `FC_CLIENT_SECRET` environment variables
- edit [server.py](server.py) (look for `_config` near the beginning of the file)

You can also configure the scopes your client should have access to, by editing server.py. Make sure that any scope you set in the client is also configured on the Feide Connect Dashboard.


### Run it

Prerequisites: you need Python 3.4+. It should come with pip3 and pyvenv.

Set up a virtual environment and install the pip3 dependencies like so:

```sh
python3 -m venv py3-env
. ./py3-env/bin/activate
pip3 install -r pip3-req.txt
```

Then you can just run the service like so:

```sh
./py-env/bin/python3 server.py [--client-id ID] [--client-secret SECRET] [-p PORT]
```

By default, the service will listen on port 8000. There are defaults for client ID and secret that are invalid and should cause Feide Connect to abort any login attempt.
