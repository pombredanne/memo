<?php

try {
  $db = new PDO('mysql:host=localhost;dbname=memo_turk', 'cf_memo', 'memo3330');
}
catch (Exception $e) {
  die($e);
}

define("MIN_SEEN", 0);
define("MIN_UNSEEN", 16); // previously 9
define("QUESTION_LIMIT", 15);
define("QUESTION_WARMUP_COUNT", 3);
?>