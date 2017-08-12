<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>Study</title>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link href="static/css/main.css" rel="stylesheet">
    <?php 
        if($webpageRedirect){
            echo '<meta http-equiv="refresh" content="'.$webpageRedirectTime.';url='.$webpageRedirectUrl.'" />';
        }
    ?>
</head>

<body>
    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
    </nav>
    <div class="container">

        <hr class="featurette-divider">
        <div class="row">
            <div class="col-lg-6"  style="text-align: justify;">
                <p><h2><?php echo $webpageMessageHeader;?></h2></p>
                <p><?php echo $webpageMessage;?></p>
            </div>
        </div>
        <hr class="featurette-divider">

    </div>
    
    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>

    <!-- Bootstrap Core JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
    
</body>

</html>
