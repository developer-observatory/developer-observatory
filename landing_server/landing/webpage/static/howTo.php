<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Study - How To</title>
    
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link href="static/css/main.css" rel="stylesheet">
    <style>
    .glyphicon.spinning {
        animation: spin 1s infinite linear;
        -webkit-animation: spin2 1s infinite linear;
    }

    @keyframes spin {
        from { transform: scale(1) rotate(0deg); }
        to { transform: scale(1) rotate(360deg); }
    }

    @-webkit-keyframes spin2 {
        from { -webkit-transform: rotate(0deg); }
        to { -webkit-transform: rotate(360deg); }
    }
    </style>
</head>
<body>
    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
    </nav>
    <div class="container">
        <hr class="featurette-divider">
        <div class="row">
            <div class="col-lg-6" style="text-align: justify;">
                <p><h2>About the online editor</h2>
For this study, you will be writing your code using a Python online editor. The editor is based on a Jupyter notebook an interactive, web-based platform that allows you to write and execute Python code directly in your browser. Please note that we use Python version 2.7.11 for this study.<br />
We have included all third party libraries that we think you might require to complete all programming tasks. 
A list of pre-installed libraries is available in the editor.</p>

<p><h2>Write your code</h2>
Before writing any code, please read the task description carefully. Type your code in shaded input cells. We have provided some skeleton code or comments for each task to help you get started. You are welcome to create any unit test code you need as you work on the task. You are also welcome to use any resources you normally would to help you solve a programming task.</p>

<p><h2>Test your code</h2>
Push the green button labeled “Run and test your code” to run your code. Possible output will be displayed below your code.</p>

<p><h2>Finishing a task</h2>
When you are satisfied with your solution, push the blue button labeled “Solved, Next Task.” The next task will appear below the task you have just finished. When you have completed the final task, the blue button will read “I am done!” Pushing this button will redirect you to our exit survey, which should take less than 15 minutes to complete. Once you choose “I am done!”, you cannot return to edit your code any further.</p>

<p><h2>If you get stuck</h2>
If you find that for any reason you are unable to complete a particular task, please push the red button labeled “NOT solved, Next Task,” which will let you tell us why you couldn’t finish the task, then continue with the next task. We appreciate your effort!<br />

If you think that the notebook got stuck, please click the yellow button labeled “Get unstuck.”<br />

<p>Please wait while we start your editor, this will only take a couple of seconds. You can start as soon as the button shows “Let me start the study.”</p>
            </div>
            <div class="col-lg-6">
                <img src="static/img/instructions_w.png" width="90%" />
            </div>
        </div>
        <button class="btn btn-lg btn-warning" id="loadingButton">
            <span class="glyphicon glyphicon-refresh spinning"></span> Preparing your notebook...    
        </button>
        <hr class="featurette-divider">
    </div>

    <!-- jQuery -->
    <script src="https://code.jquery.com/jquery-3.2.1.min.js" integrity="sha256-hwg4gsxgFZhOsEEamdOYGBf13FyQuiTwlAQgxVSNgt4=" crossorigin="anonymous"></script>

    <!-- Bootstrap Core JavaScript -->
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js" integrity="sha384-Tc5IQib027qvyjSMfHjOMaLkfuWVxZxUPnCJA7l2mCWNIpG9mGCD8wGNIcPD7Txa" crossorigin="anonymous"></script>

    <script>
    function executeQuery() {
      $.post("getAssignedInstance.php",
        {
            userid: "<?php echo $uniqid; ?>",
            token2: "<?php echo $token2; ?>"
        },
        function(data, status){
            if(data != 'error'){
                if(data.length > 5){
                    $('#loadingButton').html("Let me start the study");
                    $('#loadingButton').removeClass("btn-warning");
                    $('#loadingButton').addClass("btn-success");
                    $('#loadingButton').click(function() {
                       window.location = data;
                    });
                    //window.location = data;
                } else {
                    setTimeout(executeQuery, 5000);
                }
            } else {
                    $('#loadingButton').html("An error occured, please try again later.");
                    $('#loadingButton').removeClass("btn-warning");
                    $('#loadingButton').addClass("btn-danger");
            }
        });
    }

    // run the first time; all subsequent calls will take care of themselves
    setTimeout(executeQuery, 1000);
    </script>
</body>
</html>
