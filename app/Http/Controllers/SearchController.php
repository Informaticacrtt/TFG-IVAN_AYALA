<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Http\Requests\FormValidateRequest;
use App\User;

class SearchController extends Controller
{
 
    public function show(FormValidateRequest $request){

        if (!$request-> has('username') && !$request-> has('userID'))
            return back()->withInput();
        else {
            $result = User::checkForm($request);        
            return view('search', array('result'=> $result));
        }

        
    }

    


}
