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
         <td><?php echo round($result -> scores['cap']['english'],2).'/'.round($result -> scores['cap']['universal'],2) ;?></td>
         <td><?php echo count($result ->followers);?></td>
         <td><?php echo count($result ->friends);?></td>
    </tr>
</table>
   
</body>
</html>