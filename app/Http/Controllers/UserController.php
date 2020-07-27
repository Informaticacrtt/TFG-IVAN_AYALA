<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\User;
use App\Charts\UserChart;
class UserController extends Controller
{
   //
   	public function show(){

        $users=User::all();
        return view('user', ['users' => $users]);  
   	}

}

