import os

import orjson
import json


JSON_LIBRARY = os.environ.get('JSON_LIBRARY', 'orjson')
if JSON_LIBRARY == 'orjson':
    json_dumps = orjson.dumps
elif JSON_LIBRARY == 'stdlib':
    def json_dumps(data):
        return json.dumps(data).encode('utf-8')
else:
    raise ValueError(f"Unknown JSON_LIBRARY: {JSON_LIBRARY}")

JSON_RESPONSE = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [
        [b'content-type', b'application/json'],
    ]
}

PLAINTEXT_RESPONSE = {
    'type': 'http.response.start',
    'status': 200,
    'headers': [
        [b'content-type', b'text/plain; charset=utf-8'],
    ]
}


async def json_serialization(scope, receive, send):
    """
    Test type 1: JSON Serialization
    """
    content = json_dumps({'message': 'Hello, world!'})
    await send(JSON_RESPONSE)
    await send({
        'type': 'http.response.body',
        'body': content,
        'more_body': False
    })


async def plaintext(scope, receive, send):
    """
    Test type 2: Plaintext
    """
    content = b'Hello, world!'
    await send(PLAINTEXT_RESPONSE)
    await send({
        'type': 'http.response.body',
        'body': content,
        'more_body': False
    })


async def handle_404(scope, receive, send):
    content = b'Not found'
    await send(PLAINTEXT_RESPONSE)
    await send({
        'type': 'http.response.body',
        'body': content,
        'more_body': False
    })


routes = {
    '/json': json_serialization,
    '/plaintext': plaintext,
}


async def main(scope, receive, send):
    path = scope['path']
    handler = routes.get(path, handle_404)
    await handler(scope, receive, send)
