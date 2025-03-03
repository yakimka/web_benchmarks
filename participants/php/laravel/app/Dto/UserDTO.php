<?php

namespace App\Dto;

class UserDTO
{
    public int $id;
    public string $username;
    public string $email;
    public string $password_hash;
    public string $created_at;
    public bool $is_active;

    public function __construct($user)
    {
        $this->id = $user->id;
        $this->username = $user->username;
        $this->email = $user->email;
        $this->password_hash = $user->password_hash;
        $this->created_at = $user->created_at;
        $this->is_active = $user->is_active;
    }
}
