<?php

namespace App;

use Illuminate\Notifications\Notifiable;
use Jenssegers\Mongodb\Eloquent\Model as Eloquent;
use Illuminate\Auth\Authenticatable as AuthenticableTrait;
use Illuminate\Contracts\Auth\Authenticatable;

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

    public static function checkForm($request){
        $users=User::all(); 
        if ($request-> has('username')){
            // Search by username
            foreach ($users as $user) {
                if ($user->scores['user']['screen_name'] == $request->username)
                    return $user;
            }
            // We've to use botometer & botbusters
            
        }
        else if ($request-> has('userID')){
            // Search by id
            foreach ($users as $user) {
                if ($user->scores['user']['id_str']  == $request->userID)
                    return $user;
            }
            // We've to use botometer & botbusters
        }
    }

}
