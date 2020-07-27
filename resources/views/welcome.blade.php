<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>TFG</title>
    <link href="{{ asset('css/styles.css') }}" rel="stylesheet">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-WskhaSGFgHYWDcbwN70/dfYBj47jz9qbsMId/iRN3ewGhXQFZCSftd1LZCfmhktB" crossorigin="anonymous">
    <script src="https://kit.fontawesome.com/f3288d0e27.js" crossorigin="anonymous"></script>
</head>

<body>
    <div id="botChecker">
        <i class="fab fa-twitter-square"></i>
        <h1>Bot Checker for Twitter</h1>
        <form method="post" action="{{ route ('search') }}">
            @csrf
            <input name="username" placeholder="Username... "><br><br>
            <p>or</p>
            <input name="id" placeholder="Identifier... "><br><br>
            <button>Search</button>
        </form>
    </div>
</body>

<footer id = "footer">
    <i class="far fa-copyright"> 2020 All Rights Reserved. Author: Iván Ayala Martínez (<a href="mailto:informaticacrtt@gmail.com">informaticacrtt@gmail.com)</a></i>
</footer>

</html>