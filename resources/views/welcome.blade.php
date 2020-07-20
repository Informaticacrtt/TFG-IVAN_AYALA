<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">
    <title>TFG</title>
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
</body>
</html>