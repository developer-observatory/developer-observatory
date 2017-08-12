<?php
//! Copyright (C) 2017 Christian Stransky
//!
//! This software may be modified and distributed under the terms
//! of the MIT license.  See the LICENSE file for details.

define('__DIR__', dirname(__FILE__)); 
require_once(__DIR__."/../webpageConf/config.php");
$connect = new PDO("pgsql:host=$dbhost;dbname=$dbname", $dbuser, $dbpass);

$userId = htmlspecialchars($_GET["userId"]);
$ec2instance = htmlspecialchars($_GET["ec2instance"]);

header('content-type: application/javascript; charset=utf-8');
header("access-control-allow-origin: *");

function is_valid_callback($subject){
    // Function taken from Torleif Berger @ http://www.geekality.net/2010/06/27/php-how-to-easily-provide-json-and-jsonp/
    $identifier_syntax
      = '/^[$_\p{L}][$_\p{L}\p{Mn}\p{Mc}\p{Nd}\p{Pc}\x{200C}\x{200D}]*+$/u';

    $reserved_words = array('break', 'do', 'instanceof', 'typeof', 'case',
      'else', 'new', 'var', 'catch', 'finally', 'return', 'void', 'continue', 
      'for', 'switch', 'while', 'debugger', 'function', 'this', 'with', 
      'default', 'if', 'throw', 'delete', 'in', 'try', 'class', 'enum', 
      'extends', 'super', 'const', 'export', 'import', 'implements', 'let', 
      'private', 'public', 'yield', 'interface', 'package', 'protected', 
      'static', 'null', 'true', 'false');

    return preg_match($identifier_syntax, $subject)
        && ! in_array(strtolower($subject, 'UTF-8'), $reserved_words);
}


if(strlen($userId) == 12 and preg_match("/^[0-9a-z]+$/", $userId)){
    $sth = $connect->prepare('UPDATE "createdInstances" SET heartbeat=NOW() WHERE userid = :userid AND ec2instance = :ec2instance;');
    $sth->bindParam(':userid', $userId);
    $sth->bindParam(':ec2instance', $ec2instance);
    $sth->execute();
    if(!isset($_GET['callback'])){
        exit("{result:'ok'}");
    }
    if(is_valid_callback($_GET['callback'])){
        exit("{$_GET['callback']}({result:'ok'})");
    }
}else{
    if(!isset($_GET['callback'])){
        exit("{result:'error'}");
    }
    if(is_valid_callback($_GET['callback'])){
        exit("{$_GET['callback']}({result:'error'})");
    }
}
?>