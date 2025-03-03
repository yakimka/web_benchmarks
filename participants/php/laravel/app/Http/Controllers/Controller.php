<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Device;
use App\Dto\UserDTO;
use App\Dto\DeviceDTO;
use Illuminate\Http\Request;
use Illuminate\Routing\Controller as BaseController;

class Controller extends BaseController
{
    public function plaintext()
    {
        return response('Hello, World!', 200, ['Content-Type' => 'text/plain']);
    }

    public function api(Request $request)
    {
        $fromHeader = $request->header('X-Header');
        $fromQuery = $request->query('query');
        return response()->json([
            'message' => 'Hello, World!',
            'from_header' => $fromHeader,
            'from_query' => $fromQuery,
        ]);
    }

    public function db()
    {
        $user = User::query()->find(1);
        $devices = Device::query()->get();

        $userDTO = new UserDTO($user);
        $deviceDTOs = $devices->map(fn($device) => new DeviceDTO($device));

        return response()->json($deviceDTOs);
    }
}
