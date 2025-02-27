from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password_hash = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = "users"


class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_name = models.CharField(max_length=100)
    device_type = models.CharField(max_length=100, null=True)
    serial_number = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(null=True)
    mac_address = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=100)
    last_online = models.DateTimeField(null=True)
    purchase_date = models.DateField(null=True)
    warranty_expiry = models.DateTimeField(null=True)
    location = models.CharField(max_length=100, null=True)
    firmware_version = models.CharField(max_length=100, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "devices"
