<?php

namespace App\Http\Controllers;

use App\Http\Requests\FormValidateRequest;
use App\User;
use Khill\Lavacharts\Lavacharts;

require '../vendor/autoload.php';

use Lava;

class SearchController extends Controller
{

    public function show(FormValidateRequest $request)
    {

        if (!$request->has('username') && !$request->has('userID')) {
            return back()->withInput();
        } else {
            # We obtain user's information from our db.
            $result = User::getInfo($request);

            # First of all, we've to check if a problem occurred
            if ($result->error != "None") {
                return view('error', compact('result'));
            } else {

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
                        'width' => 400,
                        'greenFrom' => 0,
                        'greenTo' => 43,
                        'yellowFrom' => 43,
                        'yellowTo' => 80,
                        'redFrom' => 80,
                        'redTo' => 100,
                        'majorTicks' => [
                            'Human',
                            'Bot',
                        ],
                    ]
                );

                $friends_analyzed = count($result ->friends_analyzed)+count($result->friends_bots_analyzed);
                $followers_analyzed = count($result ->followers_analyzed)+count($result->followers_bots_analyzed);
                # No we have to build the charts.
                $chart = app()->chartjs
                                ->name('barChartTest')
                                ->type('bar')
                                ->size(['width' => 400, 'height' => 200])
                                ->labels(['Bot\'s comparaison from '.$friends_analyzed. ' friends & '.$followers_analyzed. ' followers analyzed.'])
                                ->datasets([
                                    [
                                        "label" => "Friends",
                                        'backgroundColor' => ['rgba(255, 99, 132, 1)'],
                                        'data' => [$friends_analyzed]
                                    ],
                                    [
                                        "label" => "Friends\'bots",
                                        'backgroundColor' => ['rgba(0, 130, 244, 1)'],
                                        'data' => [count($result->friends_bots_analyzed)]
                                    ],
                                    [
                                        "label" => "Followers",
                                        'backgroundColor' => ['rgba(244, 236, 0, 1)'],
                                        'data' => [$followers_analyzed]
                                    ],
                                    [
                                        "label" => "Followers\'bots",
                                        'backgroundColor' => ['rgba(40, 244, 0, 1)'],
                                        'data' => [count($result->followers_bots_analyzed)]
                                    ],
                                ])
                                ->options([]);
                

                # In order to obtain user's locations
                
                /*
                
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
                **/

                return view('search', compact('result', 'chart', 'temps'));
            }
        }
    }
}
