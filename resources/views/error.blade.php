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
    <div id="botChecker">
        
        <i class="fas fa-exclamation-triangle"></i>
        <h1> Error : {{$result -> Error}}</h1>
        @if ($result -> protected)
            <i class="fas fa-lock"> Account is protected</i>
        @endif
        
    </div>
</body>

<footer id = "footer">
    <i class="far fa-copyright"> 2020 All Rights Reserved. Author: Iván Ayala Martínez (<a href="mailto:informaticacrtt@gmail.com">informaticacrtt@gmail.com)</a></i>
</footer>

</html>