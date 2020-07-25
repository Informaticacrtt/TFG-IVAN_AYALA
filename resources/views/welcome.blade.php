<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>TFG</title>
    <link href="{{asset('css/app.css')}}" rel="stylesheet"> <!--Añadimos el css generado con webpack-->
</head>
<body>
    <nav>
        <h1>Bot Checker</h1>
    </nav>
    <form method="post" action="{{ route ('search') }}">
        @csrf 
        <input name="username" placeholder="Username... ">
        <p>or</p>
        <input name="id" placeholder="Identifier... "><br>
        <button>Search</button>
    </form>
    <div id="app" class="content"><!--La equita id debe ser app, como hemos visto en app.js-->
        <example-component></example-component><!--Añadimos nuestro componente vuejs-->
        <grafica-component></grafica-component>

    </div>

    <script src="{{asset('js/app.js')}}"></script> <!--Añadimos el js generado con webpack, donde se encuentra nuestro componente vuejs-->
</body>
</html>