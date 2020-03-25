<?php
//! Copyright (C) 2017 Christian Stransky
//!
//! This software may be modified and distributed under the terms
//! of the MIT license.  See the LICENSE file for details.

define('__DIR__', dirname(__FILE__)); 
require_once(__DIR__."/../webpageConf/config.php");
require_once(__DIR__."/vendor/autoload.php");


function get_ip() {
    //Just get the headers if we can or else use the SERVER global
    if ( function_exists( 'apache_request_headers' ) ) {
        $headers = apache_request_headers();
    } else {
        $headers = $_SERVER;
    }
    //Get the forwarded IP if it exists
    if ( array_key_exists( 'X-Forwarded-For', $headers ) && filter_var( $headers['X-Forwarded-For'], FILTER_VALIDATE_IP, FILTER_FLAG_IPV4 ) ) {
        $the_ip = $headers['X-Forwarded-For'];
    } elseif ( array_key_exists( 'HTTP_X_FORWARDED_FOR', $headers ) && filter_var( $headers['HTTP_X_FORWARDED_FOR'], FILTER_VALIDATE_IP, FILTER_FLAG_IPV4 )
    ) {
        $the_ip = $headers['HTTP_X_FORWARDED_FOR'];
    } else {
        
        $the_ip = filter_var( $_SERVER['REMOTE_ADDR'], FILTER_VALIDATE_IP, FILTER_FLAG_IPV4 );
    }
    return $the_ip;
}


$token = htmlspecialchars($_GET['token']);
$token2 = htmlspecialchars($_GET['token2']);

if(!(strlen($token) == 12 and preg_match("/^[0-9a-z]+$/", $token)) and (strlen($token2) == 12 and preg_match("/^[0-9a-z]+$/", $token2))){
    $webpageMessageHeader = "Invalid token";
    $webpageMessage = "Your token is invalid. Please click on the link in the E-Mail.";
    $webpageRedirect = False;
    include(__DIR__."/static/error.php");
    die();
}

if(!($_POST["age_yes"] == "on" AND $_POST["read_yes"] == "on" AND $_POST["lang_yes"] == "on" AND $_POST["cont_yes"] == "on")){

    $webpageMessageHeader = "Please accept all conditions!";
    $webpageMessage = "You have to accept all conditions to continue this study.<br />Redirecting to starting page in 5 seconds.";
    $webpageRedirect = True;
    $webpageRedirectTime = 5;
    $webpageRedirectUrl = "consent.php?token=$token&token2=$token2";
    include(__DIR__."/static/error.php");
    die();
}

if(isset($_POST["g-recaptcha-response"])){
    // Verify entered captcha is valid
    $recaptcha = new \ReCaptcha\ReCaptcha($secret);
    $remoteIp = get_ip();
    $resp = $recaptcha->verify($_POST["g-recaptcha-response"], $remoteIp);
    
    $curl = curl_init();
    curl_setopt_array($curl, array(
        CURLOPT_RETURNTRANSFER => 1,
        CURLOPT_URL => $tokenGetUrl.$token.'/'.$token2,
        CURLOPT_USERAGENT => 'LandingPage Token Verifier'
    ));
    $respToken = curl_exec($curl);
    if ($resp->isSuccess()) {
        if ($respToken == "Valid"){
            try{          
                // Connect to database
                $connect = new PDO("pgsql:host=$dbhost;dbname=$dbname", $dbuser, $dbpass);
                $connect->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
                $redisConn = new Redis();
                $redisConn->connect($redisIp);
                
                //Check if hard limit is reached:
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
                
                // Check if daily limit is reached
                $sth = $connect->prepare('SELECT COUNT(*) as count FROM "createdInstances" WHERE ip = :ip AND time >= NOW() - \'1 day\'::INTERVAL');
                $sth->bindParam(':ip', $remoteIp);
                $sth->execute();        
                $results = $sth->fetch(PDO::FETCH_ASSOC);
                //error_log($results['count']." instances started by ".$remoteIp, 0);
                if($results['count'] < $dailyMaxInstances){
                    // Generate User ID
                    $uniqid = $token;//uniqid('', true);
                    
                    /*$rare = array(2,4,6,8,3,5,7,9);
                    $common = array(0,10,13,16,19,22,1,11,14,17,20,23,12,15,18,21,24);
                    $redisRunCounter = "redisRunCounter";
                    $redisRareRunCounter = "redisRareRunCounter";
                    $redisCommonRunCounter = "redisCommonRunCounter";
                    
                    $resultsCond = 0;
                    
                    $run = $redisConn->incr($redisRunCounter);
                    if(($run % 10) == 0){
                        $rareRun = $redisConn->incr($redisRareRunCounter);
                        $resultsCond = $rare[($rareRun % count($rare))];
                    } else {
                        $commonRun = $redisConn->incr($redisCommonRunCounter);
                        $resultsCond = $common[$commonRun % count($common)];
                    }
                    
                    $sth = $connect->prepare('SELECT category FROM conditions WHERE condition = :cond;');
                    $sth->bindParam(':cond', $resultsCond);
                    $sth->execute();
                    $resultsCat = $sth->fetch(PDO::FETCH_ASSOC); */
                    
                    $sth = $connect->prepare('SELECT category, categorycount FROM (SELECT c.category as category, COUNT(ci.category) as categorycount FROM conditions c LEFT JOIN "createdInstances" ci ON c.condition = ci.condition GROUP BY c.category ORDER BY c.category) AS c ORDER BY categorycount ASC LIMIT 1;');
                    $sth->execute();        
                    $resultsCat = $sth->fetch(PDO::FETCH_ASSOC);
                    
                    $sth = $connect->prepare('SELECT cond, condcount FROM (SELECT c.condition as cond, COUNT(ci.condition) as condcount FROM conditions c LEFT JOIN "createdInstances" ci ON c.condition = ci.condition WHERE c.category = :category GROUP BY c.condition ORDER BY RANDOM()) AS f ORDER BY condcount ASC LIMIT 1;');
                    $sth->bindParam(':category', $resultsCat['category']);
                    $sth->execute();        
                    $results = $sth->fetch(PDO::FETCH_ASSOC);
                    
                    $sth = $connect->prepare('SELECT userid FROM "createdInstances" ci WHERE userid = :userid;');
                    $sth->bindParam(':userid', $token);
                    $sth->execute();        
                    $resultsUserID = $sth->fetch(PDO::FETCH_ASSOC);
                    if($resultsUserID['userid'] != $token){
                        // If token not in DB yet, then add it, otherwise skip it
                        $sth = $connect->prepare('INSERT INTO "createdInstances" (ip, time, userid, condition, category) VALUES (:ip, NOW(), :userid, :condition, :category);');
                        $sth->bindParam(':ip', $remoteIp);
                        $sth->bindParam(':userid', $token);
                        $sth->bindParam(':condition', $results['cond']);
                        // $sth->bindParam(':condition', $resultsCond);
                        $sth->bindParam(':category', $resultsCat['category']);
                        $sth->execute();
                    }
                                    
                    include("static/howTo.php");
                    ob_flush();flush();
                    

                    $serverToRunOn = $redisConn->blPop($redisQueue, $waitTimeoutForInstance);
                    
                    if ($serverToRunOn == False){
                        // Our redis hasn't delivered a server even after waiting for $waitTimeoutForInstance seconds
                        $sth = $connect->prepare('UPDATE "createdInstances" SET ec2instance = :ec2instance, instanceid = :instanceid WHERE userid = :userid;');
                        $errorIndicator = "error";
                        $sth->bindParam(':ec2instance', $errorIndicator);
                        $sth->bindParam(':userid', $token);
                        $sth->bindParam(':instanceid', $errorIndicator);
                        $sth->execute();
                    } else {
                        $serverData = explode("|||", $serverToRunOn[1]);
                        $ec2instance = $serverData[0];
                        $instanceId = $serverData[1]; 
                        $sth = $connect->prepare('UPDATE "createdInstances" SET ec2instance = :ec2instance, instanceid = :instanceid, time=NOW(), heartbeat=NOW(), condition = :condition, category = :category WHERE userid = :userid;');
                        $sth->bindParam(':ec2instance', $ec2instance);
                        $sth->bindParam(':userid', $token);
                        $sth->bindParam(':instanceid', $instanceId);
                        $sth->bindParam(':condition', $results['cond']);
                        // $sth->bindParam(':condition', $resultsCond);
                        $sth->bindParam(':category', $resultsCat['category']);
                        $sth->execute();
                        
                        $instanceIds = array();
                        $instanceIds[0] = $instanceId;
                        
                        $ec2Client = Aws\Ec2\Ec2Client::factory(array(
                            'credentials' => array(
                                'key'    => $awsAccessKey,
                                'secret' => $awsSecretKey
                            ),
                            'region' => $awsRegion, // (e.g., us-east-1)
                            'version' => 'latest'
                        ));
                        
                        // Set nametag
                        $result = $ec2Client->createTags(array(
                            'Resources' => $instanceIds,
                            'Tags' => array(
                                'Tag' => array(
                                   'Key' => 'Name',
                                   'Value' => 'StudyUser'.$token
                               )
                            )
                        ));
                        // Invalidate token
                        $curl = curl_init();
                        curl_setopt_array($curl, array(
                            CURLOPT_RETURNTRANSFER => 1,
                            CURLOPT_URL => $tokenSetUrl.$token.'/'.$token2,
                            CURLOPT_USERAGENT => 'LandingPage Token Verifier'
                        ));
                        $respToken = curl_exec($curl);
                        
                        //Let pool check run
                        exec($poolCheckCommand);
                    }
                } else {
                    $webpageMessageHeader = "Error:";
                    $webpageMessage = "You have already started to many instances, please try again in 24 hours.";
                    $webpageRedirect = False;
                    include(__DIR__."/static/error.php");
                    die();
                }
            }catch (PDOException $e) {  
                echo '<html><head><meta http-equiv="refresh" content="3;url=consent.php?token='.$token.'&token2='.$token2.'" /></head><body><h2>A database error occured, please try again! The error was: '.$e.'</h2><br/>Redirecting to starting page in 3 seconds.</body></html>';  
                die();  
            }catch (RedisException $e) { 
                $sth = $connect->prepare('UPDATE "createdInstances" SET ec2instance = :ec2instance, instanceid = :instanceid WHERE userid = :userid;');
                $errorIndicator = "error";
                echo $e;
                $sth->bindParam(':ec2instance', $errorIndicator);
                $sth->bindParam(':userid', $token);
                $sth->bindParam(':instanceid', $errorIndicator);
                $sth->execute();
                die();  
            }
        } else {
            $errors = $resp->getErrorCodes();
            $webpageMessageHeader = "Invalid Token";
            $webpageMessage = "It seems you have already participated in this study. Thank you for your help!";
            $webpageRedirect = False;
            include(__DIR__."/static/error.php");
        }
    } else {
        $errors = $resp->getErrorCodes();
        $webpageMessageHeader = "Captcha not solved correctly";
        $webpageMessage = "Please solve the captcha to prove that you are a human. Thank you for your help!<br/>Redirecting to starting page in 5 seconds.";
        $webpageRedirect = True;
        $webpageRedirectTime = 5;
        $webpageRedirectUrl = "consent.php?token=$token&token2=$token2";
        include(__DIR__."/static/error.php");
    }
}
else{
    // No Captcha entered, redirect to landing
    header("Location: consent.php?token=$token&token2=$token2");
}

?>
