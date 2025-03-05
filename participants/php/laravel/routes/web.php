<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Controller;

Route::get('/plaintext', [Controller::class, 'plaintext']);
Route::get('/api', [Controller::class, 'api']);
Route::get('/db', [Controller::class, 'db']);
