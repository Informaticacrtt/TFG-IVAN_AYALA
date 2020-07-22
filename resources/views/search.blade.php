<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Búsqueda</title>
</head>
<body>
<table>

<table>
    <tr>
        <th>USERNAME</th>
        <th>ID</th>
        <th>BOT SCORE</th>
        <th>FOLLOWERS</th>
        <th>FRIENDS</th>
    </tr>

    <tr>
        <td><?php echo $result ->scores['user']['screen_name'];?></td>
        <td><?php echo $result -> scores['user']['id_str'];?></td>
        <td><?php echo (round($result -> scores['cap']['universal'],2)*100).'%' ;?></td>
        <td><?php
            $followers = count($result ->followers);
            $followers_bots = count($result ->followers_bots);
            $total = $followers + $followers_bots; 
            echo $followers.' ('.$followers_bots/$total.'%)';?>
        </td>
        <td><?php
            $friends = count($result ->friends);
            $friends_bots = count($result ->friends_bots);
            $total = $friends + $friends_bots; 
            echo $friends.' ('.$friends_bots/$total.'%)';?>
        </td>
    </tr>
</table>
   
</body>
</html>