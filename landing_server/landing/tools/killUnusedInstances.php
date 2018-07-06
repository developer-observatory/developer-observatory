<?php
//! Copyright (C) 2017 Christian Stransky
//!
//! This software may be modified and distributed under the terms
//! of the MIT license.  See the LICENSE file for details.

define('__DIR__', dirname(__FILE__)); 
require_once(__DIR__."/../webpageConf/config.php");
require_once(__DIR__."/../html/vendor/autoload.php");

ignore_user_abort(true);

$connect = new PDO("pgsql:host=$dbhost;dbname=$dbname", $dbuser, $dbpass);
$sth = $connect->prepare('SELECT ec2instance, instanceid FROM "createdInstances" WHERE heartbeat <= NOW() - \'3 hours\'::INTERVAL AND "instanceTerminated" is false AND "terminated" is false AND instanceid != \'error\';');
$sth->execute();
$results = $sth->fetchAll(PDO::FETCH_BOTH);
$now = new DateTime();
echo("[".$now->format('Y-m-d H:i:s')."] ".count($results)." instance(s) to kill.<br />\n");
$ec2Client = Aws\Ec2\Ec2Client::factory(array(
                    'credentials' => array(
                        'key'    => $awsAccessKey,
                        'secret' => $awsSecretKey
                    ),
                    'region' => $awsRegion, // (e.g., us-east-1)
                    'version' => 'latest'
                ));
foreach ($results as $row) {
    echo($row["ec2instance"]." - ".$row["instanceid"]."<br />\n");
    try{
        $result = $ec2Client->terminateInstances(array(
            'InstanceIds' => array($row["instanceid"]),
        ));
        echo($result);
        $sth = $connect->prepare('UPDATE "createdInstances" SET "instanceTerminated" = true WHERE instanceid = :instanceid;');
        $sth->bindParam(':instanceid', $row["instanceid"]);
        $sth->execute();
    } catch (Exception $e) {
        error_log($e, 0);
    }
}
echo("-----------------------------------------------------------------------------------<br />\n");

?>