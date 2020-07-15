<!DOCTYPE html>
<html>
<head>
<style>
table {
  font-family: arial, sans-serif;
  border-collapse: collapse;
  width: 100%;
}

td, th {
  border: 1px solid #dddddd;
  text-align: left;
  padding: 8px;
}

tr:nth-child(even) {
  background-color: #dddddd;
}
</style>
</head>
<body>

<h2>HTML Table</h2>

<table>

  <tr>
    <th>ID</th>
    <th>SCORES</th>
    <th>FOLLOWERS</th>
    <th>FRIENDS</th>

  </tr>
  <?php
    foreach ( $users as $user ) {
            ?>
             <tr>
                <td><?php echo $user->id;?></td>
                <!--<td>@php
                    var_dump($user->scores);
                @endphp</td>
                <td>@php
                    var_dump($user->followers);
                @endphp</td>
                <td>@php
                    var_dump($user->friends);
                @endphp</td>-->
              </tr>
            <tr>
    <?php
    }
    ?>

</table>

</body>
</html>

