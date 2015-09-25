## aiohttp example service using Feide Connect

Minimalistic service written in Python3 using the aiohttp server.


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
