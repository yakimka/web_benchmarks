import os
from dataclasses import asdict, dataclass
from datetime import date, datetime

import falcon
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

try:
    import orjson

    json_dumps = orjson.dumps
except ImportError:
    import json

    json_dumps = json.dumps


DATABASE_URL = os.environ["DATABASE_URL"]
POOL_SIZE = 8

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


class PlaintextResource:
    def on_get(self, req, resp):
        resp.content_type = falcon.MEDIA_TEXT
        resp.text = "Hello, World!"


class ApiResource:
    def on_get(self, req, resp):
        from_query = req.params.get("query", "")
        from_header = req.headers.get("X-HEADER", "")
        resp.text = json_dumps(
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


class DbResource:
    def on_get(self, req, resp):
        users_data, devices_data = fetch_data()
        user = User(**users_data[0])
        devices = [asdict(Device(**fields)) for fields in devices_data]
        resp.text = json_dumps(devices, default=str)


app = application = falcon.App()
app.add_route("/plaintext", PlaintextResource())
app.add_route("/api", ApiResource())
app.add_route("/db", DbResource())
init_db()
