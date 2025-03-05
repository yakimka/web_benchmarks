import os
from dataclasses import asdict, dataclass
from datetime import date, datetime
from urllib.parse import parse_qs

import asyncpg
import orjson

json_dumps = orjson.dumps


DATABASE_URL = os.environ["DATABASE_URL"]
POOL_SIZE = 8

JSON_RESPONSE = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"application/json"],
    ],
}

PLAINTEXT_RESPONSE = {
    "type": "http.response.start",
    "status": 200,
    "headers": [
        [b"content-type", b"text/plain; charset=utf-8"],
    ],
}

pool = None


async def init_db():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            dsn=DATABASE_URL,
            min_size=POOL_SIZE,
            max_size=POOL_SIZE,
        )
    return pool


async def fetch_data():
    async with pool.acquire() as conn:
        users = await conn.fetch("SELECT * FROM users WHERE id = $1", 1)
        devices = await conn.fetch("SELECT * FROM devices LIMIT 10")
    return users, devices


async def plaintext(scope, receive, send):
    content = b"Hello, world!"
    await send(PLAINTEXT_RESPONSE)
    await send({"type": "http.response.body", "body": content, "more_body": False})


async def api(scope, receive, send):
    query_string = scope["query_string"]
    parsed_qs = parse_qs(query_string)

    from_header = ""
    for header in scope["headers"]:
        if header[0] == b"x-header":
            from_header = header[1].decode("utf-8")
            break
    content = json_dumps(
        {
            "message": "Hello, world!",
            "from_query": parsed_qs.get(b"query", [b""])[0].decode("utf-8"),
            "from_header": from_header,
        }
    )
    await send(JSON_RESPONSE)
    await send({"type": "http.response.body", "body": content, "more_body": False})


@dataclass
class User:
    id: int
    username: str
    email: str
    password_hash: str
    created_at: datetime
    is_active: bool


@dataclass
class Device:
    id: int
    user_id: int
    device_name: str
    device_type: str | None
    serial_number: str
    ip_address: str | None
    mac_address: str | None
    status: str
    last_online: datetime | None
    purchase_date: date | None
    warranty_expiry: datetime | None
    location: str | None
    firmware_version: str | None
    created_at: datetime


async def db(scope, receive, send):
    users_data, devices_data = await fetch_data()

    user = User(**users_data[0])
    devices = [Device(**fields) for fields in devices_data]
    content = json_dumps([asdict(device) for device in devices], default=str)
    await send(JSON_RESPONSE)
    await send({"type": "http.response.body", "body": content, "more_body": False})


routes = {
    "/plaintext": plaintext,
    "/api": api,
    "/db": db,
}


async def handle_404(scope, receive, send):
    content = b"Not found"
    await send(PLAINTEXT_RESPONSE)
    await send({"type": "http.response.body", "body": content, "more_body": False})


async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        message = await receive()
        if message["type"] == "lifespan.startup":
            await init_db()
            await send({"type": "lifespan.startup.complete"})
        return

    path = scope["path"]
    handler = routes.get(path, handle_404)
    await handler(scope, receive, send)
