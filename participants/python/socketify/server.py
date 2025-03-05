import os
from dataclasses import asdict, dataclass
from datetime import date, datetime

from socketify import App

try:
    import orjson

    json_dumps = orjson.dumps
except ImportError:
    import json

    json_dumps = json.dumps


DATABASE_URL = os.environ["DATABASE_URL"]
SQL_DRIVER = os.environ.get(
    "SQL_DRIVER", "asyncpg"
)  # asyncpg, psycopg_async, psycopg_sync
SYNC_ENDPOINTS = os.environ.get("SYNC_ENDPOINTS")
POOL_SIZE = 8

if SQL_DRIVER == "psycopg_async":
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

elif SQL_DRIVER == "psycopg_sync":
    from psycopg.rows import dict_row
    from psycopg_pool import ConnectionPool

    pool = ConnectionPool(
        DATABASE_URL,
        open=False,
        min_size=POOL_SIZE,
        max_size=POOL_SIZE,
    )

    def init_db():
        pool.open()

    def fetch_data():
        with pool.connection() as conn:
            conn.row_factory = dict_row

            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (1,))
                users = cur.fetchall()

                cur.execute("SELECT * FROM devices LIMIT 10")
                devices = cur.fetchall()
        return users, devices

elif SQL_DRIVER == "asyncpg":
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

else:
    raise ValueError(f"Invalid SQL_DRIVER value: {SQL_DRIVER}")


async def async_plaintext(res, req):
    res.end("Hello, World!")


def sync_plaintext(res, req):
    res.end("Hello, World!")


async def async_api(res, req):
    from_query = req.get_query("query")
    from_header = req.get_header("x-header")
    res.write_header("Content-Type", "application/json")
    res.cork_end(
        json_dumps(
            {
                "message": "Hello, World!",
                "from_query": from_query,
                "from_header": from_header,
            }
        )
    )


def sync_api(res, req):
    from_query = req.get_query("query")
    from_header = req.get_header("x-header")
    res.end(
        {
            "message": "Hello, World!",
            "from_query": from_query,
            "from_header": from_header,
        }
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


async def async_db(res, req):
    users_data, devices_data = await fetch_data()
    user = User(**users_data[0])
    devices = [asdict(Device(**fields)) for fields in devices_data]
    res.write_header("Content-Type", "application/json")
    res.cork_end(json_dumps(devices, default=str))


def sync_db(res, req):
    users_data, devices_data = fetch_data()
    user = User(**users_data[0])
    devices = [asdict(Device(**fields)) for fields in devices_data]
    res.write_header("Content-Type", "application/json")
    res.cork_end(json_dumps(devices, default=str))


def on_error(error, res, req):
    print("Something goes %s" % str(error))
    if res != None:
        res.write_status(500)
        res.end("Sorry we did something wrong")


def make_app(app: App):
    app.on_start(init_db)
    if SYNC_ENDPOINTS:
        app.get("/plaintext", sync_plaintext)
        app.get("/api", sync_api)
        app.get("/db", sync_db)
    else:
        app.get("/plaintext", async_plaintext)
        app.get("/api", async_api)
        app.get("/db", async_db)
    app.set_error_handler(on_error)


def run_app():
    app = App()
    make_app(app)
    app.listen(
        8000,
        lambda config: print(
            "Listening on port http://localhost:%d now\n" % config.port
        ),
    )
    app.run()


def create_fork():
    n = os.fork()
    # n greater than 0 means parent process
    if n > 0:
        return
    run_app()


WORKER_COUNT = int(os.environ.get("WEB_CONCURRENCY", 1))


for _ in range(WORKER_COUNT):
    create_fork()

run_app()
