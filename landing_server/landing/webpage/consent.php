<?php
//! Copyright (C) 2017 Christian Stransky
//!
//! This software may be modified and distributed under the terms
//! of the MIT license.  See the LICENSE file for details.

define('__DIR__', dirname(__FILE__)); 
require_once(__DIR__."/../webpageConf/config.php");

// Connect to database
$connect = new PDO("pgsql:host=$dbhost;dbname=$dbname", $dbuser, $dbpass);
$connect->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$sth = $connect->prepare('SELECT COUNT(*) as count FROM "createdInstances";');
$sth->execute();
$results = $sth->fetch(PDO::FETCH_ASSOC);
if($results['count'] > $maxInstances){
    
    $webpageMessageHeader = "Study is over";
    $webpageMessage = "Thank you for your interest! We have already received the maximum number of participants for this study.";
    $webpageRedirect = False;
    include(__DIR__."/static/error.php");
    die();
}

$token = htmlspecialchars($_GET['token']);
$token2 = htmlspecialchars($_GET['token2']);
if((strlen($token) == 12 and preg_match("/^[0-9a-z]+$/", $token)) and (strlen($token2) == 12 and preg_match("/^[0-9a-z]+$/", $token2))){
    include("static/consent.php");
}
?>