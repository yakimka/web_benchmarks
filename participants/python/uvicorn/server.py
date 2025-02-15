import os

import orjson
import json
from urllib.parse import parse_qs


JSON_LIBRARY = os.environ.get("JSON_LIBRARY", "orjson")
if JSON_LIBRARY == "orjson":
    json_dumps = orjson.dumps
elif JSON_LIBRARY == "stdlib":
    def json_dumps(data):
        return json.dumps(data).encode("utf-8")
else:
    raise ValueError(f"Unknown JSON_LIBRARY: {JSON_LIBRARY}")

JSON_RESPONSE = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"application/json"],
    ]
}

PLAINTEXT_RESPONSE = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"text/plain; charset=utf-8"],
    ]
}


async def api(scope, receive, send):
    """
    Test type 1: "API"
    """
    query_string = scope["query_string"]
    parsed_qs = parse_qs(query_string)

    from_header = ""
    for header in scope["headers"]:
        if header[0] == b"x-header":
            from_header = header[1].decode("utf-8")
            break
    content = json_dumps({
        "message": "Hello, world!",
        "from_query": parsed_qs.get(b"query", [b""])[0].decode("utf-8"),
        "from_header": from_header,
    })
    await send(JSON_RESPONSE)
    await send({
        "type": "http.response.body",
        "body": content,
        "more_body": False
    })


async def plaintext(scope, receive, send):
    """
    Test type 2: Plaintext
    """
    content = b"Hello, world!"
    await send(PLAINTEXT_RESPONSE)
    await send({
        "type": "http.response.body",
        "body": content,
        "more_body": False
    })


async def handle_404(scope, receive, send):
    content = b"Not found"
    await send(PLAINTEXT_RESPONSE)
    await send({
        "type": "http.response.body",
        "body": content,
        "more_body": False
    })


routes = {
    "/api": api,
    "/plaintext": plaintext,
}


async def main(scope, receive, send):
    path = scope["path"]
    handler = routes.get(path, handle_404)
    await handler(scope, receive, send)
