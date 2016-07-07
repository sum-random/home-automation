<HTML>
<HEAD>
<TITLE>Home page</TITLE>
</HEAD>
<BODY>
<?php 

  foreach($_SERVER as $key=>$value) 
    echo $key . " = " . $value . "<BR>\n";

  foreach(get_loaded_extensions() as $value)
    echo $value . "<BR>\n";

  $uri="http://claytontucker.com/";

  $output=file_get_contents($uri);

  echo $output;
 ?>
</BODY>
</HTML>

