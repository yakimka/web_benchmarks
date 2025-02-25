import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import date, datetime
from typing import Annotated

import asyncpg
from fastapi import FastAPI, Header, Query
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel, Field

DATABASE_URL = os.environ["DATABASE_URL"]
SYNC_ENDPOINTS = os.environ.get("SYNC_ENDPOINTS")
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await pool.close()


app = FastAPI(
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)


if SYNC_ENDPOINTS:
    @app.get("/plaintext")
    def sync_plaintext() -> str:
        return "Hello, world!"
else:
    @app.get("/plaintext")
    async def async_plaintext() -> str:
        return "Hello, world!"


if SYNC_ENDPOINTS:
    @app.get("/api")
    def sync_api(
        query: Annotated[str, Query()] = "",
        x_header: Annotated[str, Header()] = "",
    ) -> dict:
        return {
            "message": "Hello, world!",
            "from_query": query,
            "from_header": x_header,
        }
else:
    @app.get("/api")
    async def async_api(
        query: Annotated[str, Query()] = "",
        x_header: Annotated[str, Header()] = "",
    ) -> dict:
        return {
            "message": "Hello, world!",
            "from_query": query,
            "from_header": x_header,
        }


class DeviceResponse(BaseModel):
    id: int
    user_id: int
    device_name: str = Field(..., examples=["Laptop A"])
    device_type: str | None = Field(..., examples=["Laptop"])
    serial_number: str = Field(..., examples=["SN123456"])
    ip_address: str | None = Field(..., examples=["192.168.1.10"])
    mac_address: str | None = Field(..., examples=["00:1A:2B:3C:4D:5E"])
    status: str = Field(..., examples=["active"])
    last_online: datetime | None = Field(..., examples=[datetime(2022, 1, 15)])
    purchase_date: date | None = Field(..., examples=[date(2025, 1, 15)])
    warranty_expiry: datetime | None = Field(..., examples=[datetime(2025, 1, 15)])
    location: str | None = Field(..., examples=["Office"])
    firmware_version: str | None = Field(..., examples=["1.2.3"])
    created_at: datetime = Field(..., examples=[datetime(2022, 1, 15)])


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


@app.get("/db", response_model=list[DeviceResponse])
async def db() -> list[Device]:
    users_data, devices_data = await fetch_data()

    user = User(**users_data[0])
    return [Device(**fields) for fields in devices_data]
