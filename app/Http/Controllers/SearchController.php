<?php

namespace App\Http\Controllers;

use App\Http\Requests\FormValidateRequest;
use App\User;
use Khill\Lavacharts\Lavacharts;
use Illuminate\Http\Request;

require '../vendor/autoload.php';

use Lava;

class SearchController extends Controller
{

    private function getBotscore($result)
    {
        # In order to show Bot's core
        $temps = Lava::DataTable();

        $temps->addStringColumn('Type')
            ->addNumberColumn('Value')
            ->addRow(['Bot\'score (%)', $result->scores['cap']['universal'] * 100]);

        Lava::GaugeChart(
            'Chart',
            $temps,
            [
                'width' => 600,
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
    }
    private function getBotsComparaison($result)
    {

        $friends_analyzed = count($result->friends_analyzed) + count($result->friends_bots_analyzed);
        $followers_analyzed = count($result->followers_analyzed) + count($result->followers_bots_analyzed);

        $chart = app()->chartjs
            ->name('barChartTest')
            ->type('bar')
            ->size(['width' => 500, 'height' => 300])
            ->labels(['Bot\'s comparaison from ' . $friends_analyzed . ' friends & ' . $followers_analyzed . ' followers analyzed.'])
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

        return $chart;
    }

    private function getMostMentionedTwitterUsers($result)
    {
        $most_mentioned_Twitter_users  = Lava::DataTable();

        $most_mentioned_Twitter_users->addStringColumn('Most mentioned Twitter users')
            ->addNumberColumn('Count');

        foreach ($result->most_mentioned_Twitter_users as $mention) {
            $most_mentioned_Twitter_users->addRow(['@' . $mention[0],  $mention[1]]);
        }

        Lava::BarChart(
            'Most mentioned Twitter users',
            $most_mentioned_Twitter_users,
            [
                'backgroundColor' => 'transparent',
                'width' => 500,
                'height' => 400,
                'title' => 'Top 10 Most mentioned Twitter users'

            ]
        );
    }

    private function getMostUsedHashtags($result)
    {
        $hashtags  = Lava::DataTable();

        $hashtags->addStringColumn('Most used hashtags')
            ->addNumberColumn('Count');

        foreach ($result->most_used_hashtags as $hashtag) {
            $hashtags->addRow(['#' . $hashtag[0],  $hashtag[1]]);
        }

        Lava::BarChart(
            'Hashtags',
            $hashtags,
            [
                'backgroundColor' => 'transparent',
                'width' => 500,
                'height' => 400,
                'title' => 'Top 10 Most used hashtags'

            ]
        );
    }

    private function getAverageOfTweetsByDayOfWeek($result)
    {
        $average = app()->chartjs
            ->name('average_of_tweets_by_day_of_week')
            ->type('bar')
            ->size(['width' => 500, 'height' => 300])
            ->labels(['Tweets by day of week from ' . $result->average_of_tweets_by_day_of_week[7] . ' tweets analyzed.'])
            ->datasets([
                [
                    "label" => "Mon",
                    'backgroundColor' => ['rgba(255, 0, 0, 0.8)'],
                    'data' => [$result->average_of_tweets_by_day_of_week[0]]
                ],
                [
                    "label" => "Tue",
                    'backgroundColor' => ['rgba(172, 255, 51, 0.8)'],
                    'data' => [$result->average_of_tweets_by_day_of_week[1]]
                ],
                [
                    "label" => "Wed",
                    'backgroundColor' => ['rgba(51, 255, 240, 0.8)'],
                    'data' => [$result->average_of_tweets_by_day_of_week[2]]
                ],
                [
                    "label" => "Thu",
                    'backgroundColor' => ['rgba(51, 104, 255 , 0.8)'],
                    'data' => [$result->average_of_tweets_by_day_of_week[3]]
                ],
                [
                    "label" => "Fri",
                    'backgroundColor' => ['rgba(255, 141, 51, 0.8)'],
                    'data' => [$result->average_of_tweets_by_day_of_week[4]]
                ],
                [
                    "label" => "Sat",
                    'backgroundColor' => ['rgba(230, 255, 51, 0.8)'],
                    'data' => [$result->average_of_tweets_by_day_of_week[5]]
                ],
                [
                    "label" => "Sun",
                    'backgroundColor' => ['rgba(221, 51, 255, 0.8)'],
                    'data' => [$result->average_of_tweets_by_day_of_week[6]]
                ],
            ])
            ->options([]);

        return $average;
    }

    public function show(Request $request)
    {
        $request->validate([
            'username' => 'required_without:identifier',
            'identifier' => 'required_without:username',
        ]);
        if (($request->has('username') && !empty($request->input('username'))) && ($request->has('identifier') && !empty($request->input('identifier')))) {
            return redirect()->back()->withErrors(['ERROR', 'Search by username or identifier, not both.']);;
        } else {

            # We obtain user's information from our db.
            $result = User::getInfo($request);

            # First of all, we've to check if a problem occurred
            if ($result->error != "None") {
                return view('error', compact('result'));
            } else {

                # In order to show Bot's core
                $this->getBotscore($result);

                # No we have to build the charts.
                $chart = $this->getBotsComparaison($result);
                $this->getMostMentionedTwitterUsers($result);
                $this->getMostUsedHashtags($result);
                $average = $this->getAverageOfTweetsByDayOfWeek($result);

                return view('search', compact('result', 'chart', 'average'));
            }
        }
    }
}
