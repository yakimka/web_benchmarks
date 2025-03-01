import os
from dataclasses import asdict, dataclass
from datetime import date, datetime
from urllib.parse import parse_qs

DATABASE_URL = os.environ["DATABASE_URL"]
POOL_SIZE = 8

if os.environ.get("PYPY_VERSION"):
    from psycopg.rows import dict_row
    from psycopg_pool import AsyncConnectionPool

    pool = AsyncConnectionPool(
        DATABASE_URL,
        open=False,
        min_size=POOL_SIZE,
        max_size=POOL_SIZE,
    )

    async def init_db():
        await pool.open()

    async def fetch_data():
        async with pool.connection() as conn:
            conn.row_factory = dict_row

            async with conn.cursor() as cur:
                await cur.execute("SELECT * FROM users WHERE id = %s", (1,))
                users = await cur.fetchall()

                await cur.execute("SELECT * FROM devices LIMIT 10")
                devices = await cur.fetchall()
        return users, devices

else:
    import asyncpg

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


JSON_LIBRARY = os.environ.get("JSON_LIBRARY", "orjson")
if JSON_LIBRARY == "orjson":
    import orjson

    json_dumps = orjson.dumps
elif JSON_LIBRARY == "stdlib":
    import json

    def json_dumps(data, **kwargs):
        return json.dumps(data, **kwargs).encode("utf-8")

else:
    raise ValueError(f"Unknown JSON_LIBRARY: {JSON_LIBRARY}")

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
    content = json_dumps(
        {
            "message": "Hello, world!",
            "from_query": parsed_qs.get(b"query", [b""])[0].decode("utf-8"),
            "from_header": from_header,
        }
    )
    await send(JSON_RESPONSE)
    await send({"type": "http.response.body", "body": content, "more_body": False})


async def plaintext(scope, receive, send):
    """
    Test type 2: Plaintext
    """
    content = b"Hello, world!"
    await send(PLAINTEXT_RESPONSE)
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
    """
    Test type 3: Database
    """
    users_data, devices_data = await fetch_data()

    user = User(**users_data[0])
    devices = [Device(**fields) for fields in devices_data]
    content = json_dumps([asdict(device) for device in devices], default=str)
    await send(JSON_RESPONSE)
    await send({"type": "http.response.body", "body": content, "more_body": False})


async def handle_404(scope, receive, send):
    content = b"Not found"
    await send(PLAINTEXT_RESPONSE)
    await send({"type": "http.response.body", "body": content, "more_body": False})


routes = {
    "/api": api,
    "/plaintext": plaintext,
    "/db": db,
}


async def main(scope, receive, send):
    if scope["type"] == "lifespan":
        message = await receive()
        if message["type"] == "lifespan.startup":
            await init_db()
            await send({"type": "lifespan.startup.complete"})
        return

    path = scope["path"]
    handler = routes.get(path, handle_404)
    await handler(scope, receive, send)
