<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Búsqueda</title>
    <link href="{{ asset('css/styles.css') }}" rel="stylesheet">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-WskhaSGFgHYWDcbwN70/dfYBj47jz9qbsMId/iRN3ewGhXQFZCSftd1LZCfmhktB" crossorigin="anonymous">
    <script src="https://kit.fontawesome.com/f3288d0e27.js" crossorigin="anonymous"></script>


</head>

<body>

    <div id="background">
        <div id="user">
            <i class="fab fa-twitter-square"></i>
            <div id="user-info">
                <p><b>{{$result -> username}}'s statistics / ID: {{$result -> id}}<b></p>
                <p><b>Followers: {{$result -> followers}} Friends: {{$result -> friends}}</b></p>
            </div>
        </div>
        <div id = "profile">
                <p><b>
                    @if ($result -> description)
                        Description: <br>  &nbsp;{{$result -> description}}.
                    @else
                        No description available.
                    @endif
                </br></p>
                <p><b>
                    @if ($result -> url)
                        Url: <br> &nbsp;{{$result -> url}}.
                    @else
                        No url available.
                    @endif
                </b></p>
                <p><b>Created at: <br> &nbsp;{{$result -> created_at}}</br></p>
        </div>
        <div id="statistics">
            <div id="botscore">
                <div class="row d-flex justify-content-center flex-wrap" id="temps_div"></div>
                @gaugechart('Chart', 'temps_div')
            </div>
            <div id="average">
                <i class="far fa-comment-alt"></i>
                <div id="average-tweets-per-day">
                    <p><b>Average tweets per day</b></p>
                    <h1><span class="blue">{{$result -> average_tweets_per_day}}</span></h1>
                </div>
            </div>

            <div id="most_mentioned_Twitter_users">
                @if (count($result-> most_mentioned_Twitter_users)>0)

                    <p><b>Top 10 mentioned Twitter users</b></p>
                    <table align="center">
                        <thead>
                            <tr>
                                <th>User</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach ($result-> most_mentioned_Twitter_users as $user)
                            <tr>
                                <td> &#64;{{$user[0]}} </td>
                                <td> {{$user[1]}} </td>
                            </tr>
                            @endforeach
                        </tbody>
                    </table>
                @else
                    <p><b>Not mentioned Twitter users found.</b></p>

                @endif

            </div>
            <div id="most_used_hashtags">
                @if (count($result-> most_used_hashtags)>0)
                    <p><b>Top 10 used hashtags</b></p>
                    <table>
                        <thead>
                            <tr>
                                <th>Hashtag</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach ($result-> most_used_hashtags as $hashtag)
                            <tr>
                                <td> &#35;{{$hashtag[0]}} </td>
                                <td> {{$hashtag[1]}} </td>
                            </tr>
                            @endforeach
                        </tbody>
                    </table>
                @else
                    <p><b>Not hashtags found.</b></p>
                @endif

            </div>
            
            <div id="chart">
                
                @if (count($result ->followers_bots_analyzed) == 0 && count($result ->friends_bots_analyzed) == 0)
                    <p><b>This user don't have any possible bot's friends/followers.</b></p>
                    <i class="fas fa-robot"></i>
                @else
                    {!! $chart->render() !!}

                @endif
            </div>
        </div>
        <div id="location">
            @if ($result -> most_common_user_location != "")
                <p><b>Most common user location</b></p>
                <p <i class="fas fa-location-arrow"></i><b>{{$result -> most_common_user_location}}</b></p>
            @else
                <p><b>Not most common user location found.</b></p>  
            @endif
        </div>
        <script src="{{ asset('js/app.js') }}"></script>
    </div>


</body>

<footer id = "footer">
    <i class="far fa-copyright"> 2020 All Rights Reserved. Author: Iván Ayala Martínez (<a href="mailto:informaticacrtt@gmail.com">informaticacrtt@gmail.com)</a></i>
</footer>

</html>
