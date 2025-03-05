import os
from dataclasses import asdict, dataclass
from datetime import date, datetime
from urllib.parse import parse_qs

import asyncpg
import orjson

json_dumps = orjson.dumps


DATABASE_URL = os.environ["DATABASE_URL"]
POOL_SIZE = 8

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


async def plaintext(scope, proto):
    proto.response_str(
        status=200, headers=[("content-type", "text/plain")], body="Hello, world!"
    )


async def api(scope, proto):
    parsed_qs = parse_qs(scope.query_string)
    from_header = scope.headers.get("x-header", "")
    content = json_dumps(
        {
            "message": "Hello, world!",
            "from_query": parsed_qs.get("query", [""])[0],
            "from_header": from_header,
        }
    )

    proto.response_bytes(
        status=200, headers=[("content-type", "application/json")], body=content
    )


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


async def db(scope, proto):
    users_data, devices_data = await fetch_data()

    user = User(**users_data[0])
    devices = [Device(**fields) for fields in devices_data]
    content = json_dumps([asdict(device) for device in devices], default=str)
    proto.response_bytes(
        status=200, headers=[("content-type", "application/json")], body=content
    )


async def handle_404(scope, proto):
    proto.response_str(
        status=404, headers=[("content-type", "text/plain")], body="Not Found"
    )


routes = {
    "/plaintext": plaintext,
    "/api": api,
    "/db": db,
}


class App:
    def __rsgi_init__(self, loop):
        loop.run_until_complete(init_db())

    async def __rsgi__(self, scope, protocol):
        handler = routes.get(scope.path, handle_404)
        await handler(scope, protocol)


app = App()
