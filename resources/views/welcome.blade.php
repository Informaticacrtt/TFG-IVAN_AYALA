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
    <div class="botChecker">

        <div class="box">
            <i class="fab fa-twitter-square"></i>
            <h1 style="font-family: helvética;text-align: center; color:white;">Bot Checker for Twitter</h1>
            <form method="post" action="{{ route ('search') }}">
                @csrf
                <input name="username" placeholder="Username... " style="font-family: helvética;"><br><br>
                <p style="font-family: helvética;text-align: center; color:white;">or</p>
                <input name="identifier" placeholder="Identifier... " style="font-family: helvética;"><br><br>
                <button style="font-family: helvética;">Search</button>
            </form>
            @if(count($errors) > 0)
            <ul class="alert alert-danger">
                @foreach($errors->all() as $error)
                <li>{{ $error }}</li>
                @endforeach
            </ul>
            @endif
        </div>

        <footer>
            <i class="far fa-copyright"> 2020 All Rights Reserved. Author: Iván Ayala Martínez (<a href="mailto:informaticacrtt@gmail.com">informaticacrtt@gmail.com)</a></i>
        </footer>

    </div>

</body>



</html>