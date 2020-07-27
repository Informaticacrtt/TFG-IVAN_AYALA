<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Http\Requests\FormValidateRequest;
use App\User;
use ArielMejiaDev\LarapexCharts;
use Khill\Lavacharts\Lavacharts;

require '../vendor/autoload.php';

use Lava;

class SearchController extends Controller
{

    public function show(FormValidateRequest $request)
    {

        if (!$request->has('username') && !$request->has('userID'))
            return back()->withInput();
        else {
            # We obtain user's information from our db.
            $result = User::getInfo($request);
            $username = $result->scores['user']['screen_name'];

            $most_mentioned_Twitter_users =
                $id = $result->scores['user']['id_str'];
            # In order to show Bot's core
            $lava = new Lavacharts;

            $temps = $lava->DataTable();

            $temps->addStringColumn('Type')
                ->addNumberColumn('Value')
                ->addRow(['Bot\'score (%)', $result->scores['cap']['universal'] * 100]);

            Lava::GaugeChart(
                'Chart',
                $temps,
                [
                    'width'      => 400,
                    'greenFrom'  => 0,
                    'greenTo'    => 43,
                    'yellowFrom' => 43,
                    'yellowTo'   => 80,
                    'redFrom'    => 80,
                    'redTo'      => 100,
                    'majorTicks' => [
                        'Human',
                        'Bot'
                    ]
                ]
            );


            # No we have to build the charts.   
            $nfollowers = count($result->followers);
            $nfolowers_bots = count($result->followers_bots);
            $nfriends = count($result->friends);
            $nfriends_bots = count($result->friends_bots);
            $chart = app()->chartjs
                ->name('pieChartTest')
                ->type('pie')
                ->size(['width' => 400, 'height' => 200])
                ->labels(['Followers-bots(' . $nfolowers_bots . ')', 'Friends-bots(' . $nfriends_bots . ')'])
                ->datasets([
                    [
                        'backgroundColor' => ['#FF6384', '#36A2EB'],
                        'hoverBackgroundColor' => ['#FF6384', '#36A2EB'],
                        'data' => [$nfolowers_bots, $nfriends_bots]
                    ]
                ])
                ->optionsRaw("{
                
            }");

            $average_tweets_per_day = $result->Average_tweets_per_day['0'];

            # In order to obtain user's locations
            $locations = [];
            
            
            $location_user[] = $result->Most_common_user_location[0] ;



            $i = 0;
            while ($i < count($result->followers)) {
                $locations[] = $result->followers[$i]['Most_common_user_location'];
                $i++;
            }

            while ($i < count($result->friends)) {
                $locations[] = $result->friends[$i]['Most_common_user_location'];
                $i++;
            }

            $locations = array_unique($locations);




            return view('search', compact('result', 'nfollowers', 'nfriends', 'username', 'id', 'average_tweets_per_day', 'chart', 'temps', 'location_user'));
        }
    }
}
