<?php
//! Copyright (C) 2017 Christian Stransky
//!
//! This software may be modified and distributed under the terms
//! of the MIT license.  See the LICENSE file for details.

define('__DIR__', dirname(__FILE__)); 
require_once(__DIR__."/../webpageConf/config.php");

$redisConn = new Redis();
$redisConn->connect($redisIp);

$redisConn->set($redisQueueBooting, 0);
echo("Resetted boot counter\n");
?>
