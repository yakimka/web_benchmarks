from dataclasses import asdict, dataclass
from datetime import date, datetime

from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse

from .models import Device as DeviceModel
from .models import User as UserModel


async def plaintext(request):
    return HttpResponse("Hello, world!")


async def api(request):
    from_query = request.GET.get("query", "")
    from_header = request.headers.get("x-header", "")
    return JsonResponse(
        {
            "message": "Hello, world!",
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


def get_devices():
    user = UserModel.objects.get(id=1)
    User(
        id=user.id,
        username=user.username,
        email=user.email,
        password_hash=user.password_hash,
        created_at=user.created_at,
        is_active=user.is_active,
    )
    devices_from_db = DeviceModel.objects.all()[:10]
    return [
        asdict(
            Device(
                id=device.id,
                user_id=device.user_id,
                device_name=device.device_name,
                device_type=device.device_type,
                serial_number=device.serial_number,
                ip_address=device.ip_address,
                mac_address=device.mac_address,
                status=device.status,
                last_online=device.last_online,
                purchase_date=device.purchase_date,
                warranty_expiry=device.warranty_expiry,
                location=device.location,
                firmware_version=device.firmware_version,
                created_at=device.created_at,
            )
        )
        for device in devices_from_db
    ]


async def db(request):
    return JsonResponse(await sync_to_async(get_devices)(), safe=False)
