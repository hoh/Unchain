"""
Unchain your HTTP backend with authenticated WebSockets.

Publish real-time information to your clients via websocket given their
permissions set in Django/other HTTP framework.

* Subscribe via WebSocket on `ws://host/ws`
* Publish JSON via POST on `http://host/publish`
"""

import os.path
import sys
import json
import asyncio
import aiohttp
from aiohttp import web
import yaml
from collections import defaultdict
from pprint import pprint

TOKEN = lambda request: request.cookies.get('sessionid_railfleet')
BACKEND = "'http://localhost:9000/whitelist.json?token={}"

# Identity -> {Topics, Websockets}
subscriptions = defaultdict(dict)


@asyncio.coroutine
def get_identity_whitelist(token):
    """Get identity and whitelist for token from backend."""
    url = BACKEND.format(token)
    print('URL=', url)
    response_raw = yield from aiohttp.get(url)

    response = yield from response_raw.json()
    identity = response['identity']
    whitelist = response['whitelist']
    return (identity, whitelist)


@asyncio.coroutine
def register_ws(ws, token):
    """Register a WebSocket connection given an authentication
    token/session id."""
    global subscriptions

    identity, whitelist = yield from get_identity_whitelist(token)
    subs = subscriptions[identity]

    if 'whitelist' not in subs:
        subs['whitelist'] = set(whitelist)
    subs['whitelist'].update(whitelist)

    if 'connections' not in subs:
        subs['connections'] = {}
    subs['connections'][ws] = set()

    pprint(subscriptions)
    return identity


def unregister_ws(identity, ws):
    """Remove the reference to a (closed) WebSocket connection."""
    del subscriptions[identity]['connections'][ws]


def subscribe_to_topics(identity, ws, topics):
    """Subscribe the given WebSocket to a set of topics."""
    global subscriptions
    subscriptions[identity]['connections'][ws].update(topics)
    print()
    pprint(subscriptions)


@asyncio.coroutine
def index_handler(request):
    """Example index page for demo/testing."""
    index_path = os.path.join(os.path.dirname(__file__), 'index.html')
    text = open(index_path, 'r').read()
    return web.Response(body=text.encode('utf-8'))


@asyncio.coroutine
def publish_handler(request, loader=json.loads):
    """Publish POSTed data to subscribed WebSocket subscribers."""
    global subscriptions
    # data = yield from request.post()
    # print('data', data)
    msg = yield from request.json()
    print('msg', msg)

    for identity, subs in subscriptions.items():
        for ws, topics in subs['connections'].items():
            # Create a message with only topics for this user and ws:
            message = {k:v for (k,v) in msg.items()
                       if k in (subs['whitelist'] & topics)}

            if message:  # Could be empty if no topic match
                print("Sending to {}".format(identity))
                ws.send_str(json.dumps(message))

    return web.Response(body=b'OK')


@asyncio.coroutine
def websocket_handler(request):
    """Register a WebSocket connection and handle subscription to topics."""
    ws = web.WebSocketResponse()
    yield from ws.prepare(request)

    token = TOKEN(request)
    identity = yield from register_ws(ws, token)

    print('cookies', request.cookies)

    while True:
        try:
            msg = yield from ws.receive()

            if msg.tp == aiohttp.MsgType.text:
                topics = json.loads(msg.data)['topics']
                subscribe_to_topics(identity, ws, topics)

            elif msg.tp == aiohttp.MsgType.close:
                print('websocket connection closed')
                unregister_ws(identity, ws)
                break
            elif msg.tp == aiohttp.MsgType.error:
                print('ws connection closed with exception %s',
                      aio.ws.exception())
                unregister_ws(identity, ws)
                break

        except RuntimeError:
            # clients.remove(ws)
            print('client disconnected')
            break

    return ws


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index_handler)
    app.router.add_route('POST', '/publish', publish_handler)
    app.router.add_route('GET', '/ws', websocket_handler)

    srv = yield from loop.create_server(app.make_handler(),
                                        '', 8090)
    print("Server started at http://127.0.0.1:8090")
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
