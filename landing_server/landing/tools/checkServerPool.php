<?php
//! Copyright (C) 2017 Christian Stransky
//!
//! This software may be modified and distributed under the terms
//! of the MIT license.  See the LICENSE file for details.

define('__DIR__', dirname(__FILE__)); 
require_once(__DIR__."/../webpageConf/config.php");
require_once(__DIR__."/../html/vendor/autoload.php");

ignore_user_abort(true);

$redisConn = new Redis();
$redisConn->connect($redisIp);

$bootingCount = $redisConn->get($redisQueueBooting);
if($bootingCount == False or $bootingCount < 0){
    //Make sure we have no negative value here
    $redisConn->set($redisQueueBooting, 0);
}

if(($redisConn->lSize($redisQueue) + $redisConn->get($redisQueueBooting)) <= $poolSize){
    
    $ec2Client = Aws\Ec2\Ec2Client::factory(array(
                    'credentials' => array(
                        'key'    => $awsAccessKey,
                        'secret' => $awsSecretKey
                    ),
                    'region' => $awsRegion, // (e.g., us-east-1)
                    'version' => 'latest'
                ));
    
    $redisConn->incr($redisQueueBooting);
    try {
        // Create ec2 instance
        $result = $ec2Client->runInstances(array(
            'ImageId'        => $image_id,
            'MinCount'       => 1,
            'MaxCount'       => 1,
            'InstanceType'   => $instance_type,
            'KeyName'        => $sshKeyName,
            'SecurityGroupIds' => array($securityGroupID),
            //'SecurityGroupIds' => array($securityGroupId),
            'InstanceInitiatedShutdownBehavior' => 'terminate'
        ));

        $instanceIds = array($result["Instances"][0]["InstanceId"]);

        // Set nametag
        $result = $ec2Client->createTags(array(
            'Resources' => $instanceIds,
            'Tags' => array(
                'Tag' => array(
                   'Key' => 'Name',
                   'Value' => 'StudyPool'
               )
            )
        ));

        // Wait until the instance is launched
        $ec2Client->waitUntil('InstanceRunning', ['InstanceIds' => $instanceIds]);
        $result = $ec2Client->describeInstances(array(
            'InstanceIds' => $instanceIds,
        ));
                                                
        $hostname = $result["Reservations"]["0"]["Instances"]["0"]["PublicDnsName"];

        $redisConn->rPush($redisQueue, $hostname."|||".$instanceIds[0]);
    } catch (Exception $e) {
        error_log($e->getMessage(), 0);
    }
    $redisConn->decr($redisQueueBooting);
}else{
    echo("Enough instances running/booting\n");
}
?>