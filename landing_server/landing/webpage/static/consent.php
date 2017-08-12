<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>Study - Consent Form</title>
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link href="static/css/main.css" rel="stylesheet">
</head>

<body>
    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
    </nav>
    <div class="container">
        <div class="row">
            <div class="col-lg-10">
                <h1>Consent Form</h1>
            </div>
        </div>
        <hr class="featurette-divider" style="margin-top:0px;margin-bottom:10px;">
        <div class="row">
            <div class="col-lg-2">
                <p><b>Project Title:</b></p>
            </div>
            <div class="col-lg-8">
                <p>Example study</p>
            </div>
        </div>
        <div class="row">
            <div class="col-lg-2">
                <p><b>Purpose of the Study:</b></p>
            </div>
            <div class="col-lg-8">
                <p>This research is being conducted by .. at ... The purpose of this project is to give an example consent form.</p>
            </div>
        </div>
        <div class="row">
            <div class="col-lg-2">
                <p><b>Procedures:</b></p>
            </div>
            <div class="col-lg-8">
                <p> 1) You will be asked to complete several short programming tasks.<br />
                    2) Immediately after finishing the short programming tasks, you will be given an exit survey.<br />
<br />
                    The entire process should take about x minutes.
                </p>
            </div>
        </div>
        <div class="row">
            <div class="col-lg-2">
                <p><b>Potential Risks and Discomforts:</b></p>
            </div>
            <div class="col-lg-8">
                <p>...</p>
            </div>
        </div>
        <div class="row">
            <div class="col-lg-2">
                <p><b>Potential Benefits:</b></p>
            </div>
            <div class="col-lg-8">
                <p>...</p>
            </div>
        </div>
        <div class="row">
            <div class="col-lg-2">
                <p><b>Confidentiality:</b></p>
            </div>
            <div class="col-lg-8">
                <p>...</p>
            </div>
        </div>
        <div class="row">
            <div class="col-lg-2">
                <p><b>Compensation:</b></p>
            </div>
            <div class="col-lg-8">
                <p>You are not compensated for the study.</p>
            </div>
        </div>
        <div class="row">
            <div class="col-lg-2">
                <p><b>Right to Withdraw:</b></p>
            </div>
            <div class="col-lg-8">
                <p>You may choose not to take part at all. If you decide to participate in this research, you may stop participating at any time.  If you decide not to participate in this study or if you stop participating at any time, you will not be penalized or lose any benefits to which you otherwise qualify.</p>
            </div>
        </div>
        <div class="row">
            <div class="col-lg-2">
                <p><b>Participant Rights:</b></p>
            </div>
            <div class="col-lg-8">
                <p>If you have questions about your rights as a research participant or wish to report a research-related injury, please contact: <br/>
                <br/><b>
                ...
                </b>
                <br/>
                A copy of this consent form (which you should print for your records) can be found <a href="static/ConsentForm.pdf" target="_blank">here</a>.</p>
            </div>
        </div>

        <form id="form" name="form" role="form" method="post" action="howTo.php?token=<?php echo $token;?>&token2=<?php echo $token2; echo $originParam;?>">
          <div class="form-group required">
            <div class="radio">
                <label><input type="checkbox" name="age_yes" id="age_yes"> <b>I am age 18 or older.</b></label>
            </div>
          </div>
          <div class="form-group required">
            <div class="radio">
                <label><input type="checkbox" name="lang_yes"> <b>I am comfortable using the English language to participate in this study.</b></label>
            </div>
          </div>
          <div class="form-group required">
            <div class="radio">
                <label><input type="checkbox" name="read_yes"> <b>I have read this consent form or had it read to me.</b></label>
            </div>
          </div>
          <div class="form-group required">
            <div class="radio" id="cont-radio">
                <label><input type="checkbox" name="cont_yes" id="cont_yes"> <b>I agree to participate in this research and I want to continue with the study.</b></label>
            </div>
          </div>
          <div class="form-group required">
            <div class="radio">
                <label><b>Please prove that you are a human:</b> <div class="grecaptcha" id="grecaptcha"></div> </label>
            </div>
          </div>
        <button type="submit" class="btn btn-default" id="submit-btn">Submit</button>
        </form>

        <hr class="featurette-divider">

    </div>

    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>

    <!-- Bootstrap Core JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>
    
    
    <script type="text/javascript">
    
        var RC2KEY = '<?php echo $siteKey; ?>',
        doSubmit = false;

        function reCaptchaVerify(response) {
            if (response === document.querySelector('.g-recaptcha-response').value) {
                $('#submit-btn').prop('disabled', false);
            }
        }

        function reCaptchaExpired () {
            /* do something when it expires */
        }

        function reCaptchaCallback () {
            grecaptcha.render('grecaptcha', {
                'sitekey': RC2KEY,
                'callback': reCaptchaVerify,
                'expired-callback': reCaptchaExpired
            });
        }
    
        $('#submit-btn').prop('disabled', true);
        /*$("form input:checkbox").change(function () {
            $age_yes = $('input:checkbox[name=age_yes]:checked').val();
            $read_yes = $('input:checkbox[name=read_yes]:checked').val();
            $lang_yes = $('input:checkbox[name=lang_yes]:checked').val();
            $cont_yes = $('input:checkbox[name=cont_yes]:checked').val();
            if($age_yes == "on" && $read_yes == "on" && $lang_yes == "on" && $cont_yes == "on"){
                $('#submit-btn').prop('disabled', false);
            } else {
                $('#submit-btn').prop('disabled', true);
            }
        });*/
    </script>
    <script src="https://www.google.com/recaptcha/api.js?onload=reCaptchaCallback&render=explicit" async defer></script>
</body>

</html>
