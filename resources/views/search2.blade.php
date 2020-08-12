<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Búsqueda</title>
    <link href="{{ asset('css/styles.css') }}" rel="stylesheet">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-WskhaSGFgHYWDcbwN70/dfYBj47jz9qbsMId/iRN3ewGhXQFZCSftd1LZCfmhktB" crossorigin="anonymous">
    <script src="https://kit.fontawesome.com/f3288d0e27.js" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.5.0/Chart.js"></script>



</head>

<body>
    <div class="background1">
        <div class="background2">
            <div class="profile">
                <div class="profile-images">
                    <?php
                    $imageData = base64_encode(file_get_contents($result->profile_banner_url));
                    echo '<img src="data:image/jpeg;base64,' . $imageData . '" class = "background_profile">';
                    $imageData = base64_encode(file_get_contents($result->profile_image_url_https));
                    echo '<img src="data:image/jpeg;base64,' . $imageData . '" class = "photo_profile">';
                    ?>
                </div>
                <div class="username">&#64;{{$result -> screen_name}}</div>
                <div class="profile-info1">
                    <b>Followings:</b>
                    @if($result -> friends>1000 && $result -> friends<1000000) <?php echo bcdiv($result->friends, '1000', 2); ?>K @elseif ($result -> friends>1000000)
                        <?php echo bcdiv($result->friends, '1000000', 2); ?>M
                        @else
                        {{$result -> friends}}
                        @endif
                        <b>Followers:</b>
                        @if($result -> followers>1000 && $result -> followers<1000000) <?php echo bcdiv($result->followers, '1000', 2); ?>K @elseif ($result -> followers>1000000)
                            <?php echo bcdiv($result->followers, '1000000', 2); ?>M
                            @else
                            {{$result -> followers}}
                            @endif
                </div>
                <div class="profile-info2">
                    <h1>Profile</h1>
                    <p><b>Screen name: </b>{{$result -> screen_name}}</p>
                    <p><b>Display name: </b>{{$result -> name}}</p>
                    <p><b>Verified:</b>
                        @if ($result -> verified)
                        <i class="fas fa-certificate">Verified</i>
                        @else
                        Not verified
                        @endif
                    </p>
                    <p><b>Protected:</b>
                        @if ($result -> protected)
                        <i class="fas fa-user-lock">Private</i>
                        @else
                        Public <i class="fas fa-lock-open"></i>
                        @endif
                    </p>
                    <p><b>Description: </b>{{$result -> description}}</p>
                    <p><b>Location: </b>{{$result -> location}}</p>
                    <p><b>Url: </b>{{$result -> url}} </p>
                    <p><b>Date joined: </b>{{$result -> created_at}}</p>
                    <p><b>Twitter user ID: </b>{{$result -> id}}</p>
                    <p><b>Tweet languague: </b> </p>
                </div>
                <div class="botscore">
                    <div class="row d-flex justify-content-center flex-wrap" id="temps_div"></div>
                    @gaugechart('Chart', 'temps_div')
                </div>
                <div class="botscore-statistics">
                    <table>
                        <tr>
                            <th style=background-color:#f0f7fb;>English specific features</th>
                            <th style=background-color:#f0f7fb;>Language independent features</th>
                            <th style=background-color:#f0f7fb;>Bot score based on</th>
                        </tr>
                        <tr>
                            <td style=background-color:#ff5e00;><b>Content: </b>{{$result -> scores["display_scores"]["content"]}}</td>
                            <td style=background-color:#eaff00;><b>Friend: </b>{{$result -> scores["display_scores"]["friend"]}}</td>
                            <td style=background-color:#00ddff;><b>All features: </b>{{$result -> scores["display_scores"]["english"]}}</td>
                        </tr>
                        <tr>
                            <td style=background-color:#00ff66;><b>Sentiment: </b>{{$result -> scores["display_scores"]["sentiment"]}}</td>
                            <td style=background-color:#d968d3;><b>Network: </b>{{$result -> scores["display_scores"]["network"]}}</td>
                            <td style=background-color:#b8ffe6;><b>Language-independent: </b>{{$result -> scores["display_scores"]["universal"]}}</td>
                        </tr>
                        <tr>
                            <td></td>
                            <td style=background-color:#e3e8a9;><b>Temporal: </b>{{$result -> scores["display_scores"]["temporal"]}}</td>
                        </tr>
                        <tr>
                        <td></td>                            
                        <td style=background-color:#00ddff;><b>User: </b>{{$result -> scores["display_scores"]["user"]}}</td>
                        </tr>
                    </table>
                </div>

            </div>
            <div class="statistics">
                <div class="title">
                    <h1>Statistics</h1>
                </div>
                <div class="background-statistics">
                    <div class="basic-statistics">
                        <div class="basic-statistics2">
                            <p><b>Tweets (including Retweets): </b> {{$result -> statutes_count}}</p>
                            <p><b>Likes: </b>{{$result -> favourites_count}}</p>
                            <p><b>Lists: </b>{{$result -> listed_count}}</p>
                            <p><b>Retweets: </b></p>
                        </div>
                        <div class="basic-statistics2">
                            <p><b>Most recent post: </b>{{$result -> most_recent_post}}</p>
                            <p><b>Recent tweeks per day: </b>{{$result -> average_tweets_per_day}} </p>
                            <p><b>Retweet ratio: </b></p>
                            <p><b>Followers ratio: </b>{{$result -> followers_ratio}}</p>
                        </div>

                    </div>

                    <div class="barchart">
                        <div class="most_mentioned_Twitter_users">
                            @if (count($result-> most_mentioned_Twitter_users)>0)


                            <div id="poll_div2"></div>
                            @barchart('Most mentioned Twitter users', 'poll_div2')


                            @else
                            <p><b>Not mentioned Twitter users found.</b></p>

                            @endif

                        </div>
                        <div class="most_used_hashtags">

                            @if (count($result-> most_used_hashtags)>0)

                            <div id="poll_div"></div>
                            @barchart('Hashtags', 'poll_div')

                            @else
                            <p><b>Not hashtags found.</b></p>
                            @endif

                        </div>

                    </div>


                    <div class="chart">

                        <div class="friendships_analyzed">
                            @if (count($result ->followers_bots_analyzed) == 0 && count($result ->friends_bots_analyzed) == 0)
                            <p style="text-align: center;"><b>This user don't have any possible bot's friends/followers.</b><br><i class="fas fa-robot"></i></p>

                            @else
                            {!! $chart->render() !!}
                            @endif
                        </div>
                        <div class="average_of_tweets_by_day_of_week">
                            {!! $average_of_tweets_by_day_of_week_chart->render() !!}
                        </div>
                    </div>
                </div>






            </div>
        </div>
        <footer>
            <i class="far fa-copyright"> 2020 All Rights Reserved. Author: Iván Ayala Martínez (<a href="mailto:informaticacrtt@gmail.com">informaticacrtt@gmail.com)</a></i>
        </footer>
    </div>




</body>



</html>