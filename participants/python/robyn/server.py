import os
from dataclasses import asdict, dataclass
from datetime import date, datetime

from robyn import Response, Robyn, jsonify
from robyn.robyn import QueryParams

import asyncpg


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
        users = await conn.fetch('SELECT * FROM users WHERE id = $1', 1)
        devices = await conn.fetch('SELECT * FROM devices LIMIT 10')
    return users, devices


app = Robyn(__file__)
app.startup_handler(init_db)


@app.get("/plaintext")
async def plaintext(request):
    return "Hello, world!"


class GetApiParams(QueryParams):
    query: str


@app.get("/api")
async def api(request, query_params: GetApiParams):
    query = request.query_params.get("query") or ""
    x_header = request.headers.get("X-Header") or ""
    return {
        "message": "Hello, world!",
        "from_query": query,
        "from_header": x_header,
    }


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


@app.get("/db")
async def db(request):
    users_data, devices_data = await fetch_data()
    user = User(**users_data[0])
    devices = [Device(**fields) for fields in devices_data]
    return Response(
        status_code=200,
        headers={"Content-Type": "application/json"},
        description=jsonify([asdict(device) for device in devices]),
    )


app.start(host="0.0.0.0", port=8000)
