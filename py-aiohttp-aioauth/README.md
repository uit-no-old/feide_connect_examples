## aiohttp example service using Feide Connect

Minimalistic service written in Python3 using the aiohttp server. Just lets a user log in and prints some info it can get about the user.


### Configure it

Edit [server.py](server.py) and replace the client id and client secret in the config dictionary near the beginning of the file with your client id and secret. You can get a client id and secret on the [Feide Connect Dashboard](https://dashboard.feideconnect.no/).

You can also configure the scopes your client should have access to. Make sure that any scope you set in the client is also configured on the Feide Connect Dashboard.


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
./py-env/bin/python3 server.py [-p PORT]
```

By default, the service will listen on port 8000.
