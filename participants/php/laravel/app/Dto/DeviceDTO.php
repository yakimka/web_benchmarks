<?php

namespace App\Dto;

class DeviceDTO
{
    public int $id;
    public int $user_id;
    public string $device_name;
    public ?string $device_type;
    public string $serial_number;
    public ?string $ip_address;
    public ?string $mac_address;
    public string $status;
    public ?string $last_online;
    public ?string $purchase_date;
    public ?string $warranty_expiry;
    public ?string $location;
    public ?string $firmware_version;
    public string $created_at;

    public function __construct($device)
    {
        $this->id = $device->id;
        $this->user_id = $device->user_id;
        $this->device_name = $device->device_name;
        $this->device_type = $device->device_type;
        $this->serial_number = $device->serial_number;
        $this->ip_address = $device->ip_address;
        $this->mac_address = $device->mac_address;
        $this->status = $device->status;
        $this->last_online = $device->last_online;
        $this->purchase_date = $device->purchase_date;
        $this->warranty_expiry = $device->warranty_expiry;
        $this->location = $device->location;
        $this->firmware_version = $device->firmware_version;
        $this->created_at = $device->created_at;
    }
}
