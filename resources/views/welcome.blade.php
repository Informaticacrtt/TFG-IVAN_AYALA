<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    <form method="post" action="{{ route ('search') }}">
        @csrf 
        <input name="username" placeholder="@User... ">
        <input name="id" placeholder="ID... ">
        <button>Buscar</button>
    </form>
</body>
</html>