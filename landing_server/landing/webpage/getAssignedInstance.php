<?php
//! Copyright (C) 2017 Christian Stransky
//!
//! This software may be modified and distributed under the terms
//! of the MIT license.  See the LICENSE file for details.


define('__DIR__', dirname(__FILE__)); 
require_once(__DIR__."/../webpageConf/config.php");
$connect = new PDO("pgsql:host=$dbhost;dbname=$dbname", $dbuser, $dbpass);

$userId = htmlspecialchars($_POST["userid"]);
$token2 = htmlspecialchars($_POST["token2"]);

if((strlen($userId) == 12 and preg_match("/^[0-9a-z]+$/", $userId)) and (strlen($token2) == 12 and preg_match("/^[0-9a-z]+$/", $token2))){
    $sth = $connect->prepare('SELECT ec2instance as ec2instance, hash as hash FROM "createdInstances" LEFT JOIN "conditions" ON "createdInstances".condition = "conditions".condition WHERE userid = :userid;');
    $sth->bindParam(':userid', $userId);
    $sth->execute();
    $results = $sth->fetch(PDO::FETCH_BOTH);
    if(strlen($results["ec2instance"]) > 1){
        if($results["ec2instance"] == 'error'){
            echo("error");
        } else {
            $headers = get_headers("http://".$results["ec2instance"]."/nb/tree", 1);
            if ($headers[0] == 'HTTP/1.1 200 OK') {
                echo("http://".$results["ec2instance"]."/?userId=".$userId."&u=".$results["hash"]."&token=".$token2);
            } else {
                echo("br");
            }
        }
    } else {
        echo("nr");
    }
}else{
    echo("error");
}
?>