<?php

namespace App;

use Illuminate\Notifications\Notifiable;
use Jenssegers\Mongodb\Eloquent\Model as Eloquent;
use Illuminate\Auth\Authenticatable as AuthenticableTrait;
use Illuminate\Contracts\Auth\Authenticatable;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;
use DateTime;

class User extends Eloquent implements Authenticatable
{
    use AuthenticableTrait;
    use Notifiable;

    //Connection to db.
    protected $connection = 'mongodb';
    protected $collection = 'users';



    public static function getInfo($request)
    {
        // First of all, we've to check if the requested user 
        // is in our database.
        $users = User::all();
        $route = base_path() . '/userInfo.py';
        $input = NULL;
        $query = NULL;

        if ($request->has('username') && !empty($request->input('username'))) {
            $input = $request->username;
            $query = 'screen_name';
        } else {
            $input =  $request->identifier;
            $query = 'id';
        }

        // Search by input
        foreach ($users as $user) {
            if (strtoupper($user->$query) == strtoupper($input)){
                $today =  DateTime::createFromFormat('d/m/Y', date('d/m/Y'));
                $checked =  DateTime::createFromFormat('d/m/Y',$user->checked);
                $diff = $checked->diff($today);
                
                if ($diff->format('%d')==0)
                    return $user;
            }
                
        }

        // In this case, the user doesn't appear at database.
        // So, we've to use our own script in order to get all 
        // information about the requested user. 
        $process = new Process("python3  $route {$input} ");
        $process->setTimeout(3600);

        try {
            $process->mustRun();
        } catch (ProcessFailedException $exception) {
            echo $exception->getMessage();
        }

        $users = User::all();

        // Search by input
        foreach ($users as $user) {
            if (strtoupper($user->$query) == strtoupper($input))
                return $user;
        }
    }
}
