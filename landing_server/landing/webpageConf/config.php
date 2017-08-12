<?php
//! Copyright (C) 2017 Christian Stransky
//!
//! This software may be modified and distributed under the terms
//! of the MIT license.  See the LICENSE file for details.

$dailyMaxInstances = %dailyMaxInstances%;
// Hard limit, incase someone finds a way to abuse it
$maxInstances = %maxInstances%;


// Register API keys at https://www.google.com/recaptcha/admin
// These are currently test keys that will pass any verifications.
$siteKey = '%recaptchaSiteKey%';
$secret = '%recaptchaSecret%';

// AWS Credentials
$lang = '%awsLang%';
$awsAccessKey = '%awsAccessKey%';
$awsSecretKey = '%awsSecretKey%';
$awsRegion = '%awsRegion%';

// AWS Settings
$image_id  = '%awsImageId%';
$instance_type = '%awsInstanceType%';
$securityGroupID = '%awsSecurityGroupID%';
$sshKeyName = '%sshKeyName%';


// Password is being replaced automatically, skip
$dbuser = 'created_instances_user';  
$dbpass = '%pwUser1%';  
$dbhost = 'localhost';  
$dbname = 'notebook';  

$redisIp = '127.0.0.1';
$redisQueue = 'queuedInstances';
$redisQueueBooting = 'queuedInstancesBooting';
$waitTimeoutForInstance = 120;

$poolSize = %poolSize%;
$poolCheckCommand = "nohup /usr/bin/php /var/www/tools/checkServerPool.php > /dev/null 2>&1 & echo $!";

$tokenGetUrl = '%tokenGetUrl%';
$tokenSetUrl = '%tokenSetUrl%';
?>
