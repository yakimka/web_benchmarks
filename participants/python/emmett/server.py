import os
from dataclasses import dataclass
from datetime import date, datetime

from emmett import App, request  # what ?
from emmett.orm import Database, Field, Model, rowmethod
from emmett.tools import service

app = App(__name__)


class UserInDb(Model):
    tablename = "users"
    username = Field.string()
    email = Field.string()
    password_hash = Field.string()
    created_at = Field.datetime()
    is_active = Field.bool()

    @rowmethod("to_domain")
    def _to_domain(self, row):
        return User(
            id=row.id,
            username=row.username,
            email=row.email,
            password_hash=row.password_hash,
            created_at=row.created_at,
            is_active=row.is_active,
        )


class DeviceInDb(Model):
    tablename = "devices"
    user_id = Field.int()
    device_name = Field.string()
    device_type = Field.string()
    serial_number = Field.string()
    ip_address = Field.string()
    mac_address = Field.string()
    status = Field.string()
    last_online = Field.datetime()
    purchase_date = Field.date()
    warranty_expiry = Field.datetime()
    location = Field.string()
    firmware_version = Field.string()
    created_at = Field.datetime()

    @rowmethod("to_domain")
    def _to_domain(self, row):
        return Device(
            id=row.id,
            user_id=row.user_id,
            device_name=row.device_name,
            device_type=row.device_type,
            serial_number=row.serial_number,
            ip_address=row.ip_address,
            mac_address=row.mac_address,
            status=row.status,
            last_online=row.last_online,
            purchase_date=row.purchase_date,
            warranty_expiry=row.warranty_expiry,
            location=row.location,
            firmware_version=row.firmware_version,
            created_at=row.created_at,
        )


app.config.handle_static = False
app.config.db.adapter = "postgres:psycopg2"
app.config.db.host = os.environ["POSTGRES_HOST"]
app.config.db.user = "postgres"
app.config.db.password = "postgres"
app.config.db.database = "postgres"
app.config.db.pool_size = 8
db = Database(app)
db.define_models(UserInDb, DeviceInDb)


@app.route("/plaintext")
async def plaintext():
    return "Hello, world!"


@app.route("/api")
@service.json
async def api():
    return {
        "message": "Hello, world!",
        "from_query": request.query_params.query,
        "headers": request.headers.get("x-header", ""),
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


@app.route("/db", pipeline=[db.pipe])
@service.json
async def db_():
    user_from_db = UserInDb.get(1)
    user = user_from_db.to_domain()
    devices_from_db = DeviceInDb.all().select(limitby=(0, 10))

    return [device.to_domain() for device in devices_from_db]
