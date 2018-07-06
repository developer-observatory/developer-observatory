//! Copyright (C) 2017 Christian Stransky
//!
//! This software may be modified and distributed under the terms
//! of the MIT license.  See the LICENSE file for details.

function getTaskCountInNotebook(){
    return %taskCount%;
}

function heartbeatQuery() {
    var userId = document.cookie.replace(/(?:(?:^|.*;\s*)userId\s*\=\s*([^;]*).*$)|^.*$/, "$1");
    var token = document.cookie.replace(/(?:(?:^|.*;\s*)token\s*\=\s*([^;]*).*$)|^.*$/, "$1");
    $.ajax(
        {
            type: "GET",
            url: "%landingURL%/heartbeat.php?userId="+userId+"&ec2instance="+window.location.hostname+"&token="+token,
            contentType: 'text/plain',
            crossDomain: true,
            dataType: 'jsonp',
            success: function() {
                setTimeout(heartbeatQuery, 60000);
            },
            error: function() {
                setTimeout(heartbeatQuery, 60000);
            }
        }      
    );
}

var lastCopy = "";

//time measurement
var timeStampArray = {};
function timeExecMeasure(tasknum) {
    var task = tasknum.toString();
    if (typeof timeStampArray[task] == 'undefined')
        timeStampArray[task] = new Array();
    timeStampArray[task].push((new Date()).toUTCString());
}

// focus time measurement
var windowFocus = true;
$(window).focus(function() {
    windowFocus = true;
}).blur(function() {
    windowFocus = false;
});

var diffTimeFocus = 0;
var focusTime = setInterval(function() {
    if (windowFocus == true) {
        diffTimeFocus += 0.5;
    }
}, 500);

function scrollToCurrentTask(){
    id = 1 + (getCurrentTaskNumber() * 2);
    // Scroll
    window.scrollTo(0, $("#cell"+id).offset().top);
}

function submitCode(user_id, code, stat, token) {
     $.ajax({ 
        url: "/submit",
        type: "POST",
        data: JSON.stringify({"type": "code", "user_id": user_id, "code": code, "time": {"focusTime": diffTimeFocus, "execTime":JSON.stringify(timeStampArray)}, "status": stat, "token": token}),
        contentType: "application/json; charset=utf-8",
        success: function(result) {
            if(stat == 'f'){
                window.location.replace("/survey");
            }
        },
        error: function() {
            if(stat == 'f'){
                window.location.replace("/survey");
            }
        }
    });
}

function submitPastedCode(user_id, code, tasknum, cellid, token) {
    $.ajax({
        url: "/submit",
        type: "POST",
        data: JSON.stringify({'type': 'pasted', 'user_id': user_id, 'code': code, 'tasknum': tasknum, 'cellid':cellid, "token": token}),
        contentType: "application/json; charset=utf-8",
        success: function(result) {
        }
    });

}

function setCurrentTaskNumber(task){
    document.cookie = "taskNumber="+task
}

function getCurrentTaskNumber(){
    var cookieValue = document.cookie.replace(/(?:(?:^|.*;\s*)taskNumber\s*\=\s*([^;]*).*$)|^.*$/, "$1");
    if(cookieValue){
        return parseInt(cookieValue);
    }else{
        return 0;
    }
}

function hideTasks(){
    currentTask = getCurrentTaskNumber();
    if(currentTask == 0){
        $(".btn-task").hide();
        $(".btn-start").show();
    }else{
        $(".btn-task").show();
        $(".btn-start").hide();
    }
    $("#task_progress2").html(currentTask);
    for (i = 0; i <= getTaskCountInNotebook(); i++) { 
        if(currentTask < i){
            $(".task"+i).hide();
        } else {
            $(".task"+i).show();
        }
    }
    if (currentTask == getTaskCountInNotebook()){
        $(".btn-task").hide();
        $("#nextBtn").show();
        $("#nextBtn").text("I am done!");
        $("#resetBtn").show();
        $(".execBtn").show();
    }
}

// disable the overview tree in jupyter
$('div#tab_content').hide();

/*
 * Hide toolbar and menubar
 * Add the execute button
 */
$('div#menubar-container').hide();
var warningMsg = 'Are you sure you want to leave this page? '+
                    'Choosing "OK" will take you to the exit interview, '+
                    'and you will not be able to continue editing your code. '+
                    'To continue editing your code, please select "Cancel."';

$([IPython.events]).on("edit_mode.Cell", function () {
    if (IPython.notebook.get_selected_cell().cell_type == "markdown") {
        IPython.notebook.execute_selected_cells();
    }
});

define([
    'base/js/namespace',
    'base/js/promises'
], function(Jupyter, promises) {
    promises.app_initialized.then(function(appname) {
        if (appname === 'NotebookApp') {

            //IPython.notebook.kernel.restart();
            var userId = document.cookie.replace(/(?:(?:^|.*;\s*)userId\s*\=\s*([^;]*).*$)|^.*$/, "$1");
            var token = document.cookie.replace(/(?:(?:^|.*;\s*)token\s*\=\s*([^;]*).*$)|^.*$/, "$1");

            $('.cell').attr('id', function(i) {
                return 'cell'+(i+1);
            });

            // Task Progress on Header
            var taskProgress1 = $('<span/>').attr('class', 'task_progress').attr('id', 'task_progress1')
                                            .attr('style', 'color: red; font-weight: bold').html(' Current Task Progress: ');
            var taskProgress2 = $('<span/>').attr('class', 'task_progress').attr('id', 'task_progress2')
                                            .attr('style', 'color: red; font-weight: bold').html(getCurrentTaskNumber());
            var taskProgress3 = $('<span/>').attr('class', 'task_progress').attr('id', 'task_progress3')
                                            .attr('style', 'color: red; font-weight: bold').html(' out of ' + getTaskCountInNotebook());

            //Click event for skip question
            $('#skip-question-close').click(function(){
                window.location.hash = 'task' + getCurrentTaskNumber();
            });

            //Skipped task
            var answerForSkipTask = []
            $('#no-thanks').click(function(){ // no thanks button in the modal
                $('#skippedTaskModal').modal();
                IPython.notebook.save_notebook();
                if (getCurrentTaskNumber() < getTaskCountInNotebook()){
                    setCurrentTaskNumber(getCurrentTaskNumber()+1);
                    hideTasks();
                    var saved = setInterval(function() {
                        if (!IPython.notebook.dirty) {
                            clearInterval(saved);
                            submitCode(userId, IPython.notebook.toJSON(), 'n', token);
                        }
                    }, 500);
                    //update Task Progress
                    taskProgress2.html(getCurrentTaskNumber());
                    scrollToCurrentTask();
                    if (getCurrentTaskNumber() == getTaskCountInNotebook()) {
                        nextBtn.text("I am done!");
                        $('#not_solved_next_btn').remove();
                    }
                }
            });
            $('#save_widget').append(taskProgress1);
            $('#save_widget').append(taskProgress2);
            $('#save_widget').append(taskProgress3);

            var nextBtn = $('<button/>').text('Solved, Next Task').click(function() {
                IPython.notebook.save_notebook();
                if (getCurrentTaskNumber() < getTaskCountInNotebook()){
                    setCurrentTaskNumber(getCurrentTaskNumber()+1);
                    hideTasks();
                    scrollToCurrentTask();
                    console.log(getCurrentTaskNumber()+1);
                    var saved = setInterval(function() {
                        if (!IPython.notebook.dirty) {
                            clearInterval(saved);
                            submitCode(userId, IPython.notebook.toJSON(), 's', token);
                        }
                    }, 500);
                    if (getCurrentTaskNumber() == getTaskCountInNotebook()) {
                        nextBtn.text("I am done!");
                        $('#not_solved_next_btn').remove();
                    }
                    //update Task Progress
                    taskProgress2.html(getCurrentTaskNumber()); 
                } else {
                    if (confirm(warningMsg)) { 
                        var saved = setInterval(function() {
                            if (!IPython.notebook.dirty) {
                                clearInterval(saved);
                                submitCode(userId, IPython.notebook.toJSON(), 'f', token);
                            }
                        }, 500);
                    }
                }
            });
            
            nextBtn.attr('id', 'nextBtn').attr('class', 'btn btn-primary btn-task');
            nextBtn.attr('style', 'float: right;');
            $('div#notebook-container').append(nextBtn);
            
            var startBtn = $('<button/>').text('Ok, got it!').click(function() {
                setCurrentTaskNumber(getCurrentTaskNumber()+1);
                hideTasks();
                submitCode(userId, IPython.notebook.toJSON(), 'b', token);
            });
            
            startBtn.attr('id', 'startBtn').attr('class', 'btn btn-primary btn-start');
            startBtn.attr('style', 'float: right;');
            $('div#notebook-container').append(startBtn);

            // Not Solved, NEXT BUTTON
            var nsNextBtn = $('<button/>').text('NOT solved, Next Task').click(function() {
                var lib = document.cookie.replace(/(?:(?:^|.*;\s*)lib\s*\=\s*([^;]*).*$)|^.*$/, "$1");
                $('#skippedTaskModal iframe').attr({'src':'%skippedTaskSurveyURL%/?uid='+userId+'&tn='+getCurrentTaskNumber()+'&tok='+token+'&newtest=Y', 
                                            'height': 500, 'width':600});
                var naggedModal = $('#skippedTaskModal-nagged').modal();
            });
            $('#skippedTaskModal').on('shown.bs.modal', function (e) {
                $('#skippedTaskModalIFrame').on('load', function (e) {
                    $("#skippedTaskModalIFrame #Plug").hide();
                });
                })
            $('#skippedTaskModal').on('hidden.bs.modal', function (e) {
                scrollToCurrentTask()
                })
            nsNextBtn.attr('id', 'not_solved_next_btn').attr('class', 'btn btn-danger btn-task');
            nsNextBtn.attr('style','float: right;margin-right:10px;');
            $('div#notebook-container').append(nsNextBtn);

            //Run and Test
            var execBtn = $('<button/>').text('Run and Test').click(function(){
                var id = $(this).parent().attr('id');
                var cellId = parseInt(id.replace('cell',''));
                var tasknum = IPython.notebook.get_cell(cellId-1).metadata.tasknum;
                console.log(tasknum);
                timeExecMeasure(tasknum);
                // Start a timeout to select the cell before running the code.
                setTimeout(function() {
                    IPython.notebook.save_notebook();
                    IPython.notebook.execute_selected_cells();
                    var saved = setInterval(function() {
                        if (!IPython.notebook.dirty) {
                            clearInterval(saved);
                            submitCode(userId, IPython.notebook.toJSON(), 'r', token);
                        }
                    }, 500);
                });
                
                var currentdate = new Date(); 
                $("#"+id).find(".timing_area").text("Last execution started: "+currentdate.getHours() + ":" + currentdate.getMinutes() + ":" + currentdate.getSeconds())
            });
            execBtn.attr('class', 'btn btn-success btn-task execBtn');
            execBtn.attr('style', 'align-self:flex-end; width: 120px;');
            $('div.code_cell').append(execBtn);
            
            var resetBtn = $('<button/>').text('Get unstuck').attr('title', 'Use this in case that your program got stuck. This will reset all variables.').click(function(){
                //Resets the kernel
                if(confirm("Do you want to restart the kernel? This will reset all variables.")){
                    IPython.notebook.kernel.restart();
                }
            });
            resetBtn.attr('class', 'btn btn-warning btn-task').attr('id', 'resetBtn');
            resetBtn.attr('style', 'float: right;width: 110px;margin-right:10px;');
            $('div#notebook-container').append(resetBtn);
            
            var popoverText = "It looks like you pasted code into the editor. This is perfectly fine, but please let us know where you found it.";
            var id = 1;
            $('#cell'+id).addClass("task0");
            
            for (i = 1; i <= getTaskCountInNotebook(); i++) { 
                id += 1;
                $('#cell'+id).addClass("task"+i);
                $('#cell'+id+' button').addClass("task"+i);
                $('#cell'+id).append("<a name='task"+i+"'></a>");
                
                id += 1;
                $('#cell'+id).addClass("task"+i);
                $('#cell'+id+' > .input > .inner_cell').popover({content: popoverText, trigger: 'manual', delay: {show: 100, hide: 300}, animation: true, placement: 'auto'});
                $('#cell'+id+' button').addClass("task"+i);
            }
            
            var ia = $('.input_area');
            timing_area = $('<div/>')
                .attr("style", "padding: 0 5px; border: none; border-top: 1px solid #CFCFCF; font-size: 80%;")
                .attr("class", "timing_area")
                .appendTo(ia);
            
            hideTasks();
            
            /*$( "#installedLibs" ).click(function() {
                $( `<pre><b>Installed libraries and versions:</b>
        apsw==3.8.11.1.post1
        ...</pre>` ).dialog({width: "auto"});
            });*/

            //Paste behavior detection
            var numDiv = $('#notebook-container > div').length;
            for (i = 1; i <= numDiv; ++i) {
                if ($('#cell' + i + ' > button').length > 0) { //only code cell
                    $('#cell' + i).bind({
                        paste : function(e) {
                            var id = $(this).attr('id');
                            var cellId = parseInt(id.replace('cell',''));
                            var tasknum = IPython.notebook.get_cell(cellId-1).metadata.tasknum;
                            var pastedData = e.originalEvent.clipboardData.getData('text');
                            if (lastCopy.replace(/\s/g,'').includes(pastedData.replace(/\s/g,''))){
                                // Code moved around
                                console.log("Code moved")
                            } else {
                                // Get linebreaks
                                var pastedDataSplitted = pastedData.split('\n')
                                console.log("Lines pasted: "+pastedDataSplitted.length)
                                if(pastedDataSplitted.length == 1 && (pastedData.startsWith("http") || pastedData.startsWith("https") || pastedData.startsWith("www"))){
                                    console.log("URL paste detected")
                                } else {
                                    $("#"+id+"> .input > .inner_cell").popover('show');
                                    submitPastedCode(userId, pastedData, tasknum, id, token);
                                }
                            }
                        },
                        copy : function(e) {
                            // Store last copied text to avoid showing the info field while moving code around.
                            lastCopy = e.originalEvent.srcElement.value;
                        },
                        cut : function(e) {
                            var tmpCellId = e.currentTarget.id;
                            var textContent = $("#"+tmpCellId+" > .input > .inner_cell > .input_area .CodeMirror-lines")[0].innerText.split("\n");
                            var textCleaned = "";
                            var iterator = 0;
                            $.each(textContent, function(currentLine, value){
                                //Remove every 2nd line, because it contains the linenumber - no direct access to the text possible
                                iterator += 1;
                                if (iterator % 2 == 0){
                                    textCleaned += value;
                                }
                            });
                            console.log(textCleaned);
                            lastCopy = textCleaned;
                        }
                    });
                }
            }
            
            $('.inner_cell').on('shown.bs.popover', function () {
                var $pop = $(this);
                console.log($pop);
                setTimeout(function () {
                    $pop.popover('hide');
                    console.log("executed")
                }, 2500);
            });
            
            setTimeout(heartbeatQuery, 1000);
        }
    });
});

// leave at least 2 line with only a star on it below, or doc generation fails
/**
 *
 * @module IPython
 * @namespace IPython
 * @class customjs
 * @static
 */
