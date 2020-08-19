<?php

namespace App;

use Illuminate\Notifications\Notifiable;
use Jenssegers\Mongodb\Eloquent\Model as Eloquent;
use Illuminate\Auth\Authenticatable as AuthenticableTrait;
use Illuminate\Contracts\Auth\Authenticatable;
use App\Botometer;
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;

class User extends Eloquent implements Authenticatable
{
    use AuthenticableTrait;
    use Notifiable;

    //Connection to db.
    protected $connection = 'mongodb';
    protected $collection = 'users';

    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'scores', 'followers', 'friends',
    ];

    /**
     * The attributes that should be hidden for arrays.
     *
     * @var array
     */
    protected $hidden = [

    ];

    /**
     * The attributes that should be cast to native types.
     *
     * @var array
     */
    protected $casts = [
        'email_verified_at' => 'datetime',
    ];

    
    public static function getInfo($request){
        // First of all, we've to check if the requested user 
        // is in our database.
        $users=User::all();
        $route = base_path().'/userInfo.py';

        // Depend on the input, the search is different.
        if($request->has('username') && !empty($request->input('username'))){
            // Search by username
            foreach ($users as $user) {
                if (strtoupper($user->screen_name) == strtoupper($request->username))
                    return $user;
            }

            // In this case, the user doesn't appear at database.
            // So, we've to use our own script in order to get all 
            // information about the requested user. 
            $process = new Process("python3  $route {$request->username} ");
            $process->setTimeout(3600);
            
            try {
                $process->mustRun();
            
                #echo $process->getOutput();
            } catch (ProcessFailedException $exception) {
                echo $exception->getMessage();
            }

            $users=User::all();

            // Search by username
            foreach ($users as $user) {
                
                if (strtoupper($user->screen_name) == strtoupper($request->username))
                    return $user;
            }

                
        }
        else {
            // Search by id
            foreach ($users as $user) {
                if ($user-> id  == $request->identifier)
                    return $user;
            }
            // In this case, the user doesn't appear at database.
            // So, we've to use our own script in order to get all 
            // information about the requested user.   
            $process = new Process("python3 $route {$request->identifier} " );

            try {
                $process->mustRun();
            
                #echo $process->getOutput();
            } catch (ProcessFailedException $exception) {
                echo $exception->getMessage();
            }
            

            $users=User::all();

            // Search by id
            foreach ($users as $user) {
                if ($user-> id  == $request-> identifier)
                    return $user;
            }

        }
    }

 
    


}
