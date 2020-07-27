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
                <p><b>{{$username}}'s statistics / ID: {{$id}}</b></p>
                <p><b>Followers: {{$nfollowers}} Friends: {{$nfriends}}</b></p>
            </div>
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
                    <h1><span class="blue">{{$average_tweets_per_day}}</span></h1>
                </div>
            </div>

            <div id="most_mentioned_Twitter_users">
                <p><b>Top 10 mentioned Twitter users</b></p>
                <table align="center">
                    <thead>
                        <tr>
                            <th>User</th>
                            <th>Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach ($result->Most_mentioned_Twitter_users as $user)
                        <tr>
                            <td> &#64;{{$user[0]}} </td>
                            <td> {{$user[1]}} </td>
                        </tr>
                        @endforeach
                    </tbody>
                </table>

            </div>
            <div id="most_used_hashtags">
                <p><b>Top 10 used hashtags</b></p>
                <table>
                    <thead>
                        <tr>
                            <th>Hashtag</th>
                            <th>Count</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach ($result->Most_used_hashtags as $hashtag)
                        <tr>
                            <td> &#35;{{$hashtag[0]}} </td>
                            <td> {{$hashtag[1]}} </td>
                        </tr>
                        @endforeach
                    </tbody>
                </table>

            </div>
            <div id="chart">
                {!! $chart->render() !!}
                @if (count($result ->followers_bots) == 0 && count($result ->friends_bots) == 0)
                <p><b>This user don't have any possible bot's friends</b></p>
                @endif
            </div>
        </div>
        <div id="location">
            <p><b>Most common user location</b></p>
            <p <i class="fas fa-location-arrow"></i><b>{{$location_user[0]}}</b></p>
        </div>
        <script src="{{ asset('js/app.js') }}"></script>
    </div>


</body>

<footer id = "footer">
    <i class="far fa-copyright"> 2020 All Rights Reserved. Author: Iván Ayala Martínez (<a href="mailto:informaticacrtt@gmail.com">informaticacrtt@gmail.com)</a></i>
</footer>

</html>